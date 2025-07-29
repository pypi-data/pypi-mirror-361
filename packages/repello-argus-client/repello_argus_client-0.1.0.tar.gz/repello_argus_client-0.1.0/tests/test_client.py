from unittest.mock import ANY

import pytest

from repello_argus_client import ArgusClient
from repello_argus_client.enums.core import Action, InteractionType, PolicyName
from repello_argus_client.errors import (
    ArgusPermissionError,
    ArgusTypeError,
    ArgusValueError,
)
from repello_argus_client.internal.http_client import (
    PLAYGROUND_BASE_URL,
    RUNTIME_SEC_BASE_URL,
)
from repello_argus_client.types.core import Policy


@pytest.fixture
def mock_http_client(mocker):
    """Mocks the entire HttpClient class."""
    mock = mocker.patch("repello_argus_client.client.HttpClient", autospec=True)

    mock_instance = mock.return_value
    return mock_instance


@pytest.fixture
def platform_user_client(mock_http_client):
    """A client configured as a platform user (access_level=2)."""
    mock_http_client.verify_api_key.return_value = 2
    client = ArgusClient.create(
        api_key="rsk_platform_key", asset_id="asset-123", save=True
    )
    return client


@pytest.fixture
def free_user_client(mock_http_client):
    """A client configured as a free/API user (access_level=1)."""
    mock_http_client.verify_api_key.return_value = 1
    client = ArgusClient.create(api_key="sk_free_key")
    return client


def test_create_success_runtime(mock_http_client):
    """Tests successful client creation with a runtime key."""
    mock_http_client.verify_api_key.return_value = 2
    client = ArgusClient.create(api_key="rsk_test_key")

    from repello_argus_client.client import HttpClient as ClientHttpClient

    ClientHttpClient.assert_called_once_with(
        api_key="rsk_test_key", base_url=RUNTIME_SEC_BASE_URL
    )

    assert client._is_platform_user
    assert client._api_key == "rsk_test_key"


def test_create_success_playground(mock_http_client):
    """Tests successful client creation with a playground key."""
    mock_http_client.verify_api_key.return_value = 1
    client = ArgusClient.create(api_key="sk_test_key")

    from repello_argus_client.client import HttpClient as ClientHttpClient

    ClientHttpClient.assert_called_once_with(
        api_key="sk_test_key", base_url=PLAYGROUND_BASE_URL
    )
    assert not client._is_platform_user


@pytest.mark.parametrize("key", ["", None])
def test_create_no_api_key(key):
    """Tests creation failure with no API key."""

    with pytest.raises(
        (ArgusValueError, ArgusTypeError),
        match=r"(?:An API key must be provided|String should have at least 1 character|Input should be a valid string)",
    ):
        ArgusClient.create(api_key=key)


def test_create_invalid_api_key_format():
    """Tests creation failure with an invalid key prefix."""
    with pytest.raises(ArgusValueError, match="Invalid API key format."):
        ArgusClient.create(api_key="invalid_prefix_key")


def test_platform_user_init(mock_http_client):
    """Tests that platform user parameters are correctly handled."""
    mock_http_client.verify_api_key.return_value = 2
    client = ArgusClient.create(
        api_key="rsk_key", asset_id="asset-1", session_id="session-1", save=True
    )

    assert client._is_platform_user
    assert client._asset_id == "asset-1"
    assert client._session_id == "session-1"
    assert client._save
    mock_http_client.verify_asset.assert_called_once_with("asset-1")


def test_free_user_init_with_warnings(mock_http_client):
    """Tests that free users get warnings when using platform features."""
    mock_http_client.verify_api_key.return_value = 1

    with pytest.warns(UserWarning) as record:
        client = ArgusClient.create(
            api_key="sk_key", asset_id="asset-1", session_id="session-1", save=True
        )

    assert not client._is_platform_user
    assert client._asset_id is None
    assert client._session_id is None
    assert not client._save

    messages = [str(r.message) for r in record]
    assert "The 'asset_id' parameter is ignored for free plan users." in messages
    assert "The 'session_id' parameter is ignored for free plan users." in messages
    assert "The 'save' parameter is ignored for free plan users." in messages
    mock_http_client.verify_asset.assert_not_called()


def test_context_manager(platform_user_client):
    """Tests the __enter__ and __exit__ methods."""
    with platform_user_client as client:
        assert isinstance(client, ArgusClient)

    platform_user_client._http_client.close.assert_called_once()


def test_set_policies_valid(platform_user_client):
    """Tests setting a valid policy."""
    policy: Policy = {
        PolicyName.BANNED_TOPICS: {"action": Action.FLAG, "topics": ["politics"]},
        PolicyName.TOXICITY: {"action": Action.BLOCK},
    }
    platform_user_client.set_policies(policy)
    enabled_policies = platform_user_client.get_enabled_policies()

    assert enabled_policies[PolicyName.BANNED_TOPICS]["topics"] == ["politics"]
    assert enabled_policies[PolicyName.TOXICITY]["action"] == Action.BLOCK
    assert PolicyName.PII_DETECTION not in enabled_policies


def test_set_policies_invalid_config(platform_user_client):
    """Tests setting an invalid policy structure."""

    with pytest.raises(
        (ArgusValueError, ArgusTypeError),
        match=r"(?:Input should be a valid dictionary|Must be a dict with an 'action' key)",
    ):
        platform_user_client.set_policies({PolicyName.TOXICITY: "block"})


def test_set_policies_missing_metadata(platform_user_client):
    """Tests setting a policy that is missing required metadata."""
    with pytest.raises(ArgusValueError, match="missing required key: 'competitors'"):
        platform_user_client.set_policies(
            {PolicyName.COMPETITOR_MENTION: {"action": Action.FLAG}}
        )


def test_set_policies_invalid_metadata_type(platform_user_client):
    """Tests setting a policy with the wrong metadata type."""
    with pytest.raises(
        ArgusTypeError, match=r"Invalid structure in policy 'banned_topics_detection'"
    ):
        platform_user_client.set_policies(
            {PolicyName.BANNED_TOPICS: {"action": Action.FLAG, "topics": "not-a-list"}}
        )


def test_set_policies_empty_list_strict(platform_user_client):
    """Tests that an empty list for a required field raises an error in strict mode."""
    with pytest.raises(ArgusValueError, match="list 'rules' is empty"):
        platform_user_client.set_policies(
            {PolicyName.POLICY_VIOLATION: {"action": Action.BLOCK, "rules": []}}
        )


def test_set_policies_empty_list_not_strict(mock_http_client):
    """Tests that an empty list for a required field warns in non-strict mode."""
    mock_http_client.verify_api_key.return_value = 2
    client = ArgusClient.create(api_key="rsk_key", strict=False)

    with pytest.warns(UserWarning, match="list 'rules' is empty"):
        client.set_policies(
            {PolicyName.POLICY_VIOLATION: {"action": Action.BLOCK, "rules": []}}
        )

    client.set_policies(
        {PolicyName.SECRETS_KEYS: {"action": Action.BLOCK, "patterns": []}}
    )


def test_clear_policies(platform_user_client):
    """Tests clearing all policies."""
    platform_user_client.set_policies({PolicyName.TOXICITY: {"action": Action.BLOCK}})
    assert len(platform_user_client.get_enabled_policies()) == 1

    platform_user_client.clear_policies()
    assert len(platform_user_client.get_enabled_policies()) == 0


def test_check_prompt_platform_user(platform_user_client):
    """Tests check_prompt for a platform user with instance-level state."""
    platform_user_client._http_client.post_scan.return_value = {"verdict": "passed"}
    result = platform_user_client.check_prompt("Hello?")

    assert result == {"verdict": "passed"}
    platform_user_client._http_client.post_scan.assert_called_once_with(
        text="Hello?",
        interaction_type=InteractionType.PROMPT,
        asset_id="asset-123",
        session_id=None,
        save=True,
        policy=ANY,
    )


def test_check_response_platform_user_with_overrides(platform_user_client):
    """Tests check_response for a platform user with overrides."""
    policy_override: Policy = {PolicyName.TOXICITY: {"action": Action.BLOCK}}

    platform_user_client.check_response(
        "I am a response.",
        asset_id="new-asset",
        session_id="new-session",
        save=False,
        policy=policy_override,
    )

    platform_user_client._http_client.post_scan.assert_called_once()
    _, kwargs = platform_user_client._http_client.post_scan.call_args

    assert kwargs["asset_id"] == "new-asset"
    assert kwargs["session_id"] == "new-session"
    assert not kwargs["save"]
    assert kwargs["policy"][0]["policy_name"] == PolicyName.TOXICITY.value


def test_platform_user_scan_with_save_but_no_asset_id(mock_http_client):
    """Tests that saving requires an asset_id for platform users."""
    mock_http_client.verify_api_key.return_value = 2
    client = ArgusClient.create(api_key="rsk_key")

    with pytest.raises(
        ArgusValueError, match="An 'asset_id' must be provided for saving records."
    ):
        client.check_prompt("test", save=True)


def test_free_user_scan_with_policy(free_user_client):
    """Tests a scan for a free user with a valid policy."""
    policy: Policy = {PolicyName.TOXICITY: {"action": Action.BLOCK}}
    free_user_client.check_prompt("test", policy=policy)

    free_user_client._http_client.post_scan.assert_called_once()
    _, kwargs = free_user_client._http_client.post_scan.call_args

    assert kwargs["asset_id"] == "api-user-default"
    assert kwargs["session_id"] is None
    assert not kwargs["save"]


def test_free_user_scan_no_policy(free_user_client):
    """Tests that a free user scan fails without an active policy."""
    with pytest.raises(
        ArgusValueError, match="API users must provide at least one active policy."
    ):
        free_user_client.check_prompt("test")


@pytest.mark.parametrize(
    "check_method_name, policy_name, expected_interaction_type, required_arg_key, required_arg_value",
    [
        (
            "check_policy_violation",
            PolicyName.POLICY_VIOLATION,
            InteractionType.PROMPT,
            "rules",
            ["rule1"],
        ),
        (
            "check_competitor_mention",
            PolicyName.COMPETITOR_MENTION,
            InteractionType.RESPONSE,
            "competitors",
            ["c1"],
        ),
        ("check_pii", PolicyName.PII_DETECTION, InteractionType.PROMPT, None, None),
        ("check_toxicity", PolicyName.TOXICITY, InteractionType.RESPONSE, None, None),
    ],
)
def test_methods_with_dynamic_interaction_type(
    free_user_client,
    check_method_name,
    policy_name,
    expected_interaction_type,
    required_arg_key,
    required_arg_value,
):
    """Tests check methods that take interaction_type as a direct argument."""
    free_user_client._http_client.post_scan.return_value = {"verdict": "passed"}
    method_to_call = getattr(free_user_client, check_method_name)

    method_args = ["text", expected_interaction_type, Action.BLOCK]

    method_kwargs = {}
    if required_arg_key:
        method_kwargs[required_arg_key] = required_arg_value

    method_to_call(*method_args, **method_kwargs)

    free_user_client._http_client.post_scan.assert_called_once()
    _, kwargs = free_user_client._http_client.post_scan.call_args

    assert kwargs["text"] == "text"
    assert kwargs["interaction_type"] == expected_interaction_type
    assert kwargs["policy"][0]["policy_name"] == policy_name.value
    assert kwargs["policy"][0]["action"] == Action.BLOCK.value

    if required_arg_key:
        assert kwargs["policy"][0]["metadata"] == required_arg_value
    else:
        assert kwargs["policy"][0]["metadata"] == ""


@pytest.mark.parametrize(
    "check_method_name, policy_name, expected_interaction_type, required_arg_key, required_arg_value",
    [
        (
            "check_banned_topics",
            PolicyName.BANNED_TOPICS,
            InteractionType.PROMPT,
            "topics",
            ["t1"],
        ),
        (
            "check_prompt_injection",
            PolicyName.PROMPT_INJECTION,
            InteractionType.PROMPT,
            None,
            None,
        ),
        (
            "check_unsafe_prompt",
            PolicyName.UNSAFE_PROMPT,
            InteractionType.PROMPT,
            None,
            None,
        ),
        (
            "check_secrets_keys",
            PolicyName.SECRETS_KEYS,
            InteractionType.RESPONSE,
            "patterns",
            [],
        ),
        (
            "check_unsafe_response",
            PolicyName.UNSAFE_RESPONSE,
            InteractionType.RESPONSE,
            None,
            None,
        ),
        (
            "check_system_prompt_leak",
            PolicyName.SYSTEM_PROMPT_LEAK,
            InteractionType.RESPONSE,
            "system_prompt",
            "secret",
        ),
    ],
)
def test_methods_with_fixed_interaction_type(
    free_user_client,
    check_method_name,
    policy_name,
    expected_interaction_type,
    required_arg_key,
    required_arg_value,
):
    """Tests check methods that have a hardcoded interaction_type."""
    free_user_client._http_client.post_scan.return_value = {"verdict": "passed"}
    method_to_call = getattr(free_user_client, check_method_name)

    method_args = ["text", Action.BLOCK]

    method_kwargs = {}
    if required_arg_key:
        method_kwargs[required_arg_key] = required_arg_value

    method_to_call(*method_args, **method_kwargs)

    free_user_client._http_client.post_scan.assert_called_once()
    _, kwargs = free_user_client._http_client.post_scan.call_args

    assert kwargs["text"] == "text"
    assert kwargs["interaction_type"] == expected_interaction_type
    assert kwargs["policy"][0]["policy_name"] == policy_name.value
    assert kwargs["policy"][0]["action"] == Action.BLOCK.value

    if required_arg_key:
        assert kwargs["policy"][0]["metadata"] == required_arg_value
    else:
        assert kwargs["policy"][0]["metadata"] == ""


def test_check_secrets_keys_default_patterns(free_user_client):
    """Tests that check_secrets_keys provides a default empty list for patterns."""
    free_user_client.check_secrets_keys("text", Action.FLAG)

    _, kwargs = free_user_client._http_client.post_scan.call_args
    policy_sent = kwargs["policy"][0]
    assert policy_sent["metadata"] == []


def test_asset_id_methods_platform_user(platform_user_client):
    """Tests asset_id methods for a platform user."""
    assert platform_user_client.get_asset_id() == "asset-123"

    platform_user_client.set_asset_id("new-asset")
    platform_user_client._http_client.verify_asset.assert_called_with("new-asset")
    assert platform_user_client.get_asset_id() == "new-asset"

    platform_user_client.clear_asset_id()
    assert platform_user_client.get_asset_id() is None


def test_asset_id_methods_free_user(free_user_client):
    """Tests that asset_id methods are no-ops for free users."""
    with pytest.raises(
        ArgusPermissionError, match=r"only available for Platform users"
    ):
        free_user_client.set_asset_id("some-asset")

    with pytest.raises(
        ArgusPermissionError, match=r"only available for Platform users"
    ):
        free_user_client.get_asset_id()

    with pytest.raises(
        ArgusPermissionError, match=r"only available for Platform users"
    ):
        free_user_client.clear_asset_id()


def test_session_id_methods_platform_user(platform_user_client):
    """Tests session_id methods for a platform user."""
    assert platform_user_client.get_session_id() is None

    platform_user_client.set_session_id("session-abc")
    assert platform_user_client.get_session_id() == "session-abc"

    platform_user_client.clear_session_id()
    assert platform_user_client.get_session_id() is None


def test_session_id_methods_free_user_not_strict(mock_http_client):
    """Tests that session_id methods warn for free users in non-strict mode."""
    mock_http_client.verify_api_key.return_value = 1
    client = ArgusClient.create(api_key="sk_key", strict=False)

    with pytest.warns(UserWarning, match="only available for Platform users"):
        client.set_session_id("some-session")

    with pytest.warns(UserWarning, match="only available for Platform users"):
        client.get_session_id()

    with pytest.warns(UserWarning, match="only available for Platform users"):
        client.clear_session_id()
