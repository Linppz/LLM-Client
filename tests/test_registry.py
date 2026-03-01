def test_render_and_log(prompt_registry, tmp_path):
    role = {
        "lanuage": "c++",
        "role": "猪",
        "your_code": "cout << I Love you",
        "output_schema": "{}",
    }

    prompt_registry.render_and_log(role, "code_review.j2")
    assert len(prompt_registry.audit_logs) == 1
    assert prompt_registry.audit_logs[0].template_name == "code_review.j2"


def test_version_hash_stability(prompt_registry, tmp_path):
    role = {
        "lanuage": "c++",
        "role": "猪",
        "your_code": "cout << I Love you",
        "output_schema": "{}",
    }
    role1 = {
        "lanuage": "c++",
        "role": "猪",
        "your_code": "cout << I Love you",
        "output_schema": "{}",
    }

    prompt_registry.render_and_log(role, "code_review.j2")
    prompt_registry.render_and_log(role1, "code_review.j2")
    assert (
        prompt_registry.audit_logs[0].version_hash
        == prompt_registry.audit_logs[1].version_hash
    )


def test_get_version(prompt_registry, tmp_path):
    role = {
        "lanuage": "c++",
        "role": "猪",
        "your_code": "cout << I Love you",
        "output_schema": "{}",
    }
    prompt_registry.render_and_log(role, "code_review.j2")
    number = prompt_registry.get(
        "code_review.j2", prompt_registry.data["code_review.j2"][0].version_hash
    )
    assert number.version_hash == prompt_registry.data["code_review.j2"][0].version_hash


def test_diff_versions(prompt_registry, tmp_path):
    role = {
        "lanuage": "c++",
        "role": "猪",
        "your_code": "cout << I Love you",
        "output_schema": "{}",
    }
    role1 = {
        "lanuage": "c++",
        "role": "猪",
        "your_code": "cout << I Love ydou",
        "output_schema": "{}",
    }

    prompt_registry.render_and_log(role, "code_review.j2")
    prompt_registry.render_and_log(role1, "code_review.j2")

    assert (
        prompt_registry.diff(
            "code_review.j2",
            prompt_registry.data["code_review.j2"][0].version_hash,
            prompt_registry.data["code_review.j2"][1].version_hash,
        )
        is not None
    )
