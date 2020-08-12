from pytask import main


def test_marker_is_configured(tmp_path):
    session = main({"paths": tmp_path})

    assert "latex" in session.config["markers"]
