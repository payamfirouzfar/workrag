from career_os.browser.field_mapping import is_sensitive, map_field
from career_os.browser.safety import detect_blocker


def test_map_field_identifies_common_labels():
    assert map_field("First Name") == "identity.first_name"
    assert map_field("email_address") == "identity.email"
    assert map_field("LinkedIn Profile URL") == "identity.linkedin"


def test_map_field_returns_none_for_unknown_label():
    assert map_field("favorite color") is None


def test_sensitive_questions_are_flagged():
    assert is_sensitive("Do you now or will you in the future require sponsorship?")
    assert is_sensitive("Are you legally authorized to work in this country?")
    assert is_sensitive("What is your expected salary?")


def test_non_sensitive_questions_are_not_flagged():
    assert not is_sensitive("What is your full name?")
    assert not is_sensitive("Please attach your resume")


def test_detect_blocker_finds_captcha():
    result = detect_blocker("Please complete the reCAPTCHA to continue")
    assert result is not None
    assert result.blocker_type == "CAPTCHA"


def test_detect_blocker_finds_mfa():
    result = detect_blocker("Enter the verification code sent to your phone")
    assert result is not None
    assert result.blocker_type == "MFA"


def test_detect_blocker_returns_none_for_clean_page():
    assert detect_blocker("Apply now for this exciting role") is None
