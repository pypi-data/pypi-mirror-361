from unittest import mock

from briefcase.config import AppConfig


def test_no_resources(create_command):
    """If the template defines no extra targets, none are installed."""
    myapp = AppConfig(
        app_name="my-app",
        formal_name="My App",
        bundle="com.example",
        version="1.2.3",
        description="This is a simple app",
        sources=["src/my_app"],
        license={"file": "LICENSE"},
    )

    # Prime the path index with no targets
    create_command._briefcase_toml[myapp] = {"paths": {}}

    install_image = mock.MagicMock()
    create_command.install_image = install_image

    # Install app resources
    create_command.install_app_resources(myapp)

    # No icons or document types, so no calls to install images
    install_image.assert_not_called()


def test_icon_target(create_command, tmp_path):
    """If the template defines an icon target, it will be installed."""
    myapp = AppConfig(
        app_name="my-app",
        formal_name="My App",
        bundle="com.example",
        version="1.2.3",
        description="This is a simple app",
        sources=["src/my_app"],
        icon="images/icon",
        license={"file": "LICENSE"},
    )

    # Prime the path index with 2 icon targets
    create_command._briefcase_toml[myapp] = {
        "paths": {
            "icon": {
                "10": "path/to/icon-10.png",
                "20": "path/to/icon-20.png",
            }
        }
    }

    install_image = mock.MagicMock()
    create_command.install_image = install_image

    # Install app resources
    create_command.install_app_resources(myapp)

    # 2 calls to install icons will be made
    install_image.assert_has_calls(
        [
            mock.call(
                "application icon",
                source="images/icon",
                variant=None,
                size="10",
                target=tmp_path
                / "base_path"
                / "build"
                / "my-app"
                / "tester"
                / "dummy"
                / "path"
                / "to"
                / "icon-10.png",
            ),
            mock.call(
                "application icon",
                source="images/icon",
                variant=None,
                size="20",
                target=tmp_path
                / "base_path"
                / "build"
                / "my-app"
                / "tester"
                / "dummy"
                / "path"
                / "to"
                / "icon-20.png",
            ),
        ],
        any_order=True,
    )


def test_icon_variant_target(create_command, tmp_path):
    """If the template defines an icon target with variants, they will be installed."""
    myapp = AppConfig(
        app_name="my-app",
        formal_name="My App",
        bundle="com.example",
        version="1.2.3",
        description="This is a simple app",
        sources=["src/my_app"],
        icon={
            "round": "images/round",
            "square": "images/square",
        },
        license={"file": "LICENSE"},
    )

    # Prime the path index with 2 icon targets
    create_command._briefcase_toml[myapp] = {
        "paths": {
            "icon": {
                "round": "path/to/round.png",
                "square": {
                    "10": "path/to/square-10.png",
                    "20": "path/to/square-20.png",
                },
            }
        }
    }

    install_image = mock.MagicMock()
    create_command.install_image = install_image

    # Install app resources
    create_command.install_app_resources(myapp)

    # 3 calls to install icons will be made
    install_image.assert_has_calls(
        [
            mock.call(
                "application icon",
                source={"round": "images/round", "square": "images/square"},
                variant=None,
                size="round",  # This is expected for unsized variants
                target=tmp_path
                / "base_path"
                / "build"
                / "my-app"
                / "tester"
                / "dummy"
                / "path"
                / "to"
                / "round.png",
            ),
            mock.call(
                "application icon",
                source={"round": "images/round", "square": "images/square"},
                variant="square",
                size="10",
                target=tmp_path
                / "base_path"
                / "build"
                / "my-app"
                / "tester"
                / "dummy"
                / "path"
                / "to"
                / "square-10.png",
            ),
            mock.call(
                "application icon",
                source={"round": "images/round", "square": "images/square"},
                variant="square",
                size="20",
                target=tmp_path
                / "base_path"
                / "build"
                / "my-app"
                / "tester"
                / "dummy"
                / "path"
                / "to"
                / "square-20.png",
            ),
        ],
        any_order=True,
    )


def test_splash_target(create_command, capsys):
    """If the template defines a splash target, a warning will be raised."""
    myapp = AppConfig(
        app_name="my-app",
        formal_name="My App",
        bundle="com.example",
        version="1.2.3",
        description="This is a simple app",
        sources=["src/my_app"],
        splash="images/splash",
        license={"file": "LICENSE"},
    )

    # Prime an empty path index
    create_command._briefcase_toml[myapp] = {"paths": {}}

    install_image = mock.MagicMock()
    create_command.install_image = install_image

    # Install app resources
    create_command.install_app_resources(myapp)

    # No calls to install splashes are made
    install_image.assert_not_called()

    # A warning about the splash configuration was raised.
    assert "The splash configuration will be ignored." in capsys.readouterr().out


def test_splash_variant_target(create_command, capsys):
    """If the template defines a splash target with variants, a warning is raised."""
    myapp = AppConfig(
        app_name="my-app",
        formal_name="My App",
        bundle="com.example",
        version="1.2.3",
        description="This is a simple app",
        sources=["src/my_app"],
        splash={
            "portrait": "images/portrait",
            "landscape": "images/landscape",
        },
        license={"file": "LICENSE"},
    )

    # Prime an empty path index
    create_command._briefcase_toml[myapp] = {"paths": {}}

    install_image = mock.MagicMock()
    create_command.install_image = install_image

    # Install app resources
    create_command.install_app_resources(myapp)

    # No calls to install splashes are made
    install_image.assert_not_called()

    # A warning about the splash configuration was raised.
    assert "The splash configuration will be ignored." in capsys.readouterr().out


def test_doctype_icon_target(create_command, tmp_path):
    """If the template defines document types, their icons will be installed."""
    myapp = AppConfig(
        app_name="my-app",
        formal_name="My App",
        bundle="com.example",
        version="1.2.3",
        description="This is a simple app",
        sources=["src/my_app"],
        document_type={
            "mydoc": {
                "icon": "images/mydoc-icon",
                "description": "mydoc image",
                "url": "https://testexample.com",
                "extension": "mydoc",
            },
            "other": {
                "icon": "images/other-icon",
                "description": "other image",
                "url": "https://othertestexample.com",
                "extension": "other",
            },
        },
        license={"file": "LICENSE"},
    )

    # Prime the path index with 2 document types;
    # * mydoc, which has a single static image; and
    # * other, which has multiple size targets.
    create_command._briefcase_toml[myapp] = {
        "paths": {
            "document_type_icon": {
                "mydoc": "path/to/mydoc-icon.png",
                "other": {
                    "10": "path/to/other-icon-10.png",
                    "20": "path/to/other-icon-20.png",
                },
            }
        }
    }

    install_image = mock.MagicMock()
    create_command.install_image = install_image

    # Install app resources
    create_command.install_app_resources(myapp)

    # 2 calls to install doctype icon images will be made
    install_image.assert_has_calls(
        [
            mock.call(
                "icon for .mydoc documents",
                source="images/mydoc-icon",
                variant=None,
                size=None,
                target=tmp_path
                / "base_path"
                / "build"
                / "my-app"
                / "tester"
                / "dummy"
                / "path"
                / "to"
                / "mydoc-icon.png",
            ),
            mock.call(
                "icon for .other documents",
                source="images/other-icon",
                variant=None,
                size="10",
                target=tmp_path
                / "base_path"
                / "build"
                / "my-app"
                / "tester"
                / "dummy"
                / "path"
                / "to"
                / "other-icon-10.png",
            ),
            mock.call(
                "icon for .other documents",
                source="images/other-icon",
                variant=None,
                size="20",
                target=tmp_path
                / "base_path"
                / "build"
                / "my-app"
                / "tester"
                / "dummy"
                / "path"
                / "to"
                / "other-icon-20.png",
            ),
        ],
        any_order=True,
    )
