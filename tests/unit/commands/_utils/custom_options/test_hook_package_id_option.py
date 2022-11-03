from unittest import TestCase
from unittest.mock import MagicMock, patch
import os

import click

from samcli.commands._utils.custom_options.hook_package_id_option import HookPackageIdOption
from samcli.lib.hook.exceptions import InvalidHookWrapperException


class TestHookPackageIdOption(TestCase):
    def setUp(self):
        self.name = "hook-package-id"
        self.opt = "--hook-package-id"
        self.terraform = "terraform"

    @patch("samcli.commands._utils.custom_options.hook_package_id_option.get_available_hook_packages_ids")
    @patch("samcli.lib.hook.hook_wrapper.IacHookWrapper._load_hook_package")
    def test_invalid_hook_package_id(self, load_hook_package_mock, get_available_hook_packages_ids_mock):
        hook_package_id = "not_supported"
        available_hook_packages = ["terraform", "cdk"]
        load_hook_package_mock.side_effect = InvalidHookWrapperException(
            f'Cannot locate hook package with hook_package_id "{hook_package_id}"'
        )
        get_available_hook_packages_ids_mock.return_value = available_hook_packages

        hook_package_id_option = HookPackageIdOption(
            param_decls=(self.name, self.opt),
            force_prepare=False,
            invalid_coexist_options=[],
        )
        ctx = MagicMock()
        ctx.command.name = "invoke"
        opts = {"hook_package_id": hook_package_id}
        args = []
        with self.assertRaises(click.BadParameter) as e:
            hook_package_id_option.handle_parse_result(ctx, opts, args)

        self.assertEqual(
            e.exception.message,
            f"{hook_package_id} is not a valid hook package id."
            f"{os.linesep}valid package ids: {available_hook_packages}",
        )

    @patch("samcli.commands._utils.custom_options.hook_package_id_option.IacHookWrapper")
    def test_invalid_coexist_options(self, iac_hook_wrapper_mock):

        invalid_coexist_options = ["t", "template", "template-file", "parameters-override"]
        iac_hook_wrapper_instance_mock = MagicMock()
        iac_hook_wrapper_mock.return_value = iac_hook_wrapper_instance_mock

        hook_package_id_option = HookPackageIdOption(
            param_decls=(self.name, self.opt),
            force_prepare=False,
            invalid_coexist_options=invalid_coexist_options,
        )
        ctx = MagicMock()
        opts = {"hook_package_id": self.terraform, "template_file": "any/path/template.yaml"}
        args = []
        with self.assertRaises(click.BadParameter) as e:
            hook_package_id_option.handle_parse_result(ctx, opts, args)

        self.assertEqual(
            e.exception.message,
            f"Parameters hook-package-id, and {','.join(invalid_coexist_options)} cannot be used together",
        )

    @patch("samcli.commands._utils.custom_options.hook_package_id_option.update_experimental_context")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.prompt_experimental")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.os.getcwd")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.IacHookWrapper")
    def test_valid_hook_package_with_only_hook_id_option(
        self, iac_hook_wrapper_mock, getcwd_mock, prompt_experimental_mock, update_experimental_context_mock
    ):
        metadata_path = "path/metadata.json"
        cwd_path = "path/current"
        invalid_coexist_options = ["t", "template", "template-file", "parameters-override"]

        iac_hook_wrapper_instance_mock = MagicMock()
        iac_hook_wrapper_instance_mock.prepare.return_value = metadata_path
        iac_hook_wrapper_mock.return_value = iac_hook_wrapper_instance_mock
        prompt_experimental_mock.return_value = True

        getcwd_mock.return_value = cwd_path

        hook_package_id_option = HookPackageIdOption(
            param_decls=(self.name, self.opt),
            force_prepare=True,
            invalid_coexist_options=invalid_coexist_options,
        )
        ctx = MagicMock()
        opts = {
            "hook_package_id": self.terraform,
        }
        args = []
        hook_package_id_option.handle_parse_result(ctx, opts, args)
        iac_hook_wrapper_instance_mock.prepare.assert_called_once_with(
            os.path.join(cwd_path, ".aws-sam-iacs", "iacs_metadata"), cwd_path, False, None, None
        )
        self.assertEqual(opts.get("template_file"), metadata_path)

    @patch("samcli.commands._utils.custom_options.hook_package_id_option.update_experimental_context")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.prompt_experimental")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.os.getcwd")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.IacHookWrapper")
    def test_valid_hook_package_with_other_options(
        self, iac_hook_wrapper_mock, getcwd_mock, prompt_experimental_mock, update_experimental_context_mock
    ):

        metadata_path = "path/metadata.json"
        cwd_path = "path/current"
        invalid_coexist_options = ["t", "template", "template-file", "parameters-override"]

        iac_hook_wrapper_instance_mock = MagicMock()
        iac_hook_wrapper_instance_mock.prepare.return_value = metadata_path
        iac_hook_wrapper_mock.return_value = iac_hook_wrapper_instance_mock
        prompt_experimental_mock.return_value = True

        getcwd_mock.return_value = cwd_path

        hook_package_id_option = HookPackageIdOption(
            param_decls=(self.name, self.opt),
            force_prepare=True,
            invalid_coexist_options=invalid_coexist_options,
        )
        ctx = MagicMock()
        opts = {
            "hook_package_id": self.terraform,
            "debug": True,
            "profile": "test",
            "region": "us-east-1",
        }
        args = []
        hook_package_id_option.handle_parse_result(ctx, opts, args)
        iac_hook_wrapper_instance_mock.prepare.assert_called_once_with(
            os.path.join(cwd_path, ".aws-sam-iacs", "iacs_metadata"),
            cwd_path,
            True,
            "test",
            "us-east-1",
        )
        self.assertEqual(opts.get("template_file"), metadata_path)

    @patch("samcli.commands._utils.custom_options.hook_package_id_option.update_experimental_context")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.prompt_experimental")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.os.getcwd")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.os.path.exists")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.IacHookWrapper")
    def test_valid_hook_package_with_skipping_prepare_hook_and_built_path_exists(
        self,
        iac_hook_wrapper_mock,
        path_exists_mock,
        getcwd_mock,
        prompt_experimental_mock,
        update_experimental_context_mock,
    ):

        metadata_path = "path/metadata.json"
        cwd_path = "path/current"
        invalid_coexist_options = ["t", "template", "template-file", "parameters-override"]

        iac_hook_wrapper_instance_mock = MagicMock()
        iac_hook_wrapper_instance_mock.prepare.return_value = metadata_path
        iac_hook_wrapper_mock.return_value = iac_hook_wrapper_instance_mock
        prompt_experimental_mock.return_value = True

        getcwd_mock.return_value = cwd_path

        path_exists_mock.return_value = True

        hook_package_id_option = HookPackageIdOption(
            param_decls=(self.name, self.opt),
            force_prepare=False,
            invalid_coexist_options=invalid_coexist_options,
        )
        ctx = MagicMock()
        opts = {
            "hook_package_id": self.terraform,
        }
        args = []
        hook_package_id_option.handle_parse_result(ctx, opts, args)
        iac_hook_wrapper_instance_mock.prepare.assert_not_called()
        self.assertEqual(opts.get("template_file"), None)

    @patch("samcli.commands._utils.custom_options.hook_package_id_option.GlobalConfig")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.update_experimental_context")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.prompt_experimental")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.os.getcwd")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.os.path.exists")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.IacHookWrapper")
    def test_valid_hook_package_with_disable_terraform_beta_feature(
        self,
        iac_hook_wrapper_mock,
        path_exists_mock,
        getcwd_mock,
        prompt_experimental_mock,
        update_experimental_context_mock,
        global_config_mock,
    ):

        metadata_path = "path/metadata.json"
        cwd_path = "path/current"
        invalid_coexist_options = ["t", "template", "template-file", "parameters-override"]

        iac_hook_wrapper_instance_mock = MagicMock()
        iac_hook_wrapper_instance_mock.prepare.return_value = metadata_path
        iac_hook_wrapper_mock.return_value = iac_hook_wrapper_instance_mock
        prompt_experimental_mock.return_value = False
        gc_mock = MagicMock()
        global_config_mock.return_value = gc_mock
        gc_mock.get_value.return_value = False

        getcwd_mock.return_value = cwd_path

        hook_package_id_option = HookPackageIdOption(
            param_decls=(self.name, self.opt),
            force_prepare=True,
            invalid_coexist_options=invalid_coexist_options,
        )
        ctx = MagicMock()
        ctx.default_map = {}
        opts = {
            "hook_package_id": self.terraform,
        }
        args = []
        hook_package_id_option.handle_parse_result(ctx, opts, args)
        iac_hook_wrapper_instance_mock.prepare.assert_not_called()
        self.assertEqual(opts.get("template_file"), None)

    @patch("samcli.commands._utils.custom_options.hook_package_id_option.update_experimental_context")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.prompt_experimental")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.os.getcwd")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.os.path.exists")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.IacHookWrapper")
    def test_valid_hook_package_with_no_beta_feature_option(
        self,
        iac_hook_wrapper_mock,
        path_exists_mock,
        getcwd_mock,
        prompt_experimental_mock,
        update_experimental_context_mock,
    ):

        metadata_path = "path/metadata.json"
        cwd_path = "path/current"
        invalid_coexist_options = ["t", "template", "template-file", "parameters-override"]

        iac_hook_wrapper_instance_mock = MagicMock()
        iac_hook_wrapper_instance_mock.prepare.return_value = metadata_path
        iac_hook_wrapper_mock.return_value = iac_hook_wrapper_instance_mock
        prompt_experimental_mock.return_value = False

        getcwd_mock.return_value = cwd_path

        hook_package_id_option = HookPackageIdOption(
            param_decls=(self.name, self.opt),
            force_prepare=True,
            invalid_coexist_options=invalid_coexist_options,
        )
        ctx = MagicMock()
        opts = {
            "hook_package_id": self.terraform,
            "beta_features": False,
        }
        args = []
        hook_package_id_option.handle_parse_result(ctx, opts, args)
        prompt_experimental_mock.assert_not_called()
        iac_hook_wrapper_instance_mock.prepare.assert_not_called()
        self.assertEqual(opts.get("template_file"), None)

    @patch("samcli.commands._utils.custom_options.hook_package_id_option.update_experimental_context")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.prompt_experimental")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.os.getcwd")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.os.path.exists")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.IacHookWrapper")
    def test_valid_hook_package_with_beta_feature_option(
        self,
        iac_hook_wrapper_mock,
        path_exists_mock,
        getcwd_mock,
        prompt_experimental_mock,
        update_experimental_context_mock,
    ):

        metadata_path = "path/metadata.json"
        cwd_path = "path/current"
        invalid_coexist_options = ["t", "template", "template-file", "parameters-override"]

        iac_hook_wrapper_instance_mock = MagicMock()
        iac_hook_wrapper_instance_mock.prepare.return_value = metadata_path
        iac_hook_wrapper_mock.return_value = iac_hook_wrapper_instance_mock
        prompt_experimental_mock.return_value = False

        getcwd_mock.return_value = cwd_path

        hook_package_id_option = HookPackageIdOption(
            param_decls=(self.name, self.opt),
            force_prepare=True,
            invalid_coexist_options=invalid_coexist_options,
        )
        ctx = MagicMock()
        opts = {
            "hook_package_id": self.terraform,
            "beta_features": True,
        }
        args = []
        hook_package_id_option.handle_parse_result(ctx, opts, args)
        prompt_experimental_mock.assert_not_called()
        iac_hook_wrapper_instance_mock.prepare.assert_called_once_with(
            os.path.join(cwd_path, ".aws-sam-iacs", "iacs_metadata"),
            cwd_path,
            False,
            None,
            None,
        )
        self.assertEqual(opts.get("template_file"), metadata_path)

    @patch("samcli.commands._utils.custom_options.hook_package_id_option.update_experimental_context")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.prompt_experimental")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.os.getcwd")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.os.path.exists")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.IacHookWrapper")
    def test_valid_hook_package_with_beta_feature_option_in_sam_config(
        self,
        iac_hook_wrapper_mock,
        path_exists_mock,
        getcwd_mock,
        prompt_experimental_mock,
        update_experimental_context_mock,
    ):
        metadata_path = "path/metadata.json"
        cwd_path = "path/current"
        invalid_coexist_options = ["t", "template", "template-file", "parameters-override"]

        iac_hook_wrapper_instance_mock = MagicMock()
        iac_hook_wrapper_instance_mock.prepare.return_value = metadata_path
        iac_hook_wrapper_mock.return_value = iac_hook_wrapper_instance_mock
        prompt_experimental_mock.return_value = False

        getcwd_mock.return_value = cwd_path

        hook_package_id_option = HookPackageIdOption(
            param_decls=(self.name, self.opt),
            force_prepare=True,
            invalid_coexist_options=invalid_coexist_options,
        )
        ctx = MagicMock()
        ctx.default_map = {"beta_features": True}
        opts = {
            "hook_package_id": self.terraform,
        }
        args = []
        hook_package_id_option.handle_parse_result(ctx, opts, args)
        prompt_experimental_mock.assert_not_called()
        iac_hook_wrapper_instance_mock.prepare.assert_called_once_with(
            os.path.join(cwd_path, ".aws-sam-iacs", "iacs_metadata"),
            cwd_path,
            False,
            None,
            None,
        )
        self.assertEqual(opts.get("template_file"), metadata_path)

    @patch("samcli.commands._utils.custom_options.hook_package_id_option.GlobalConfig")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.update_experimental_context")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.prompt_experimental")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.os.getcwd")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.os.path.exists")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.IacHookWrapper")
    def test_valid_hook_package_with_beta_feature_option_in_environment_variable(
        self,
        iac_hook_wrapper_mock,
        path_exists_mock,
        getcwd_mock,
        prompt_experimental_mock,
        update_experimental_context_mock,
        global_config_mock,
    ):
        metadata_path = "path/metadata.json"
        cwd_path = "path/current"
        invalid_coexist_options = ["t", "template", "template-file", "parameters-override"]

        iac_hook_wrapper_instance_mock = MagicMock()
        iac_hook_wrapper_instance_mock.prepare.return_value = metadata_path
        iac_hook_wrapper_mock.return_value = iac_hook_wrapper_instance_mock
        prompt_experimental_mock.return_value = False

        getcwd_mock.return_value = cwd_path

        hook_package_id_option = HookPackageIdOption(
            param_decls=(self.name, self.opt),
            force_prepare=True,
            invalid_coexist_options=invalid_coexist_options,
        )
        ctx = MagicMock()
        ctx.default_map = {}
        opts = {
            "hook_package_id": self.terraform,
        }
        gc_mock = MagicMock()
        global_config_mock.return_value = gc_mock
        gc_mock.get_value.return_value = True
        args = []
        hook_package_id_option.handle_parse_result(ctx, opts, args)
        prompt_experimental_mock.assert_not_called()
        iac_hook_wrapper_instance_mock.prepare.assert_called_once_with(
            os.path.join(cwd_path, ".aws-sam-iacs", "iacs_metadata"),
            cwd_path,
            False,
            None,
            None,
        )
        self.assertEqual(opts.get("template_file"), metadata_path)

    @patch("samcli.commands._utils.custom_options.hook_package_id_option.update_experimental_context")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.prompt_experimental")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.os.getcwd")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.os.path.exists")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.IacHookWrapper")
    def test_valid_hook_package_with_skipping_prepare_hook_and_built_path_doesnot_exist(
        self,
        iac_hook_wrapper_mock,
        path_exists_mock,
        getcwd_mock,
        prompt_experimental_mock,
        update_experimental_context_mock,
    ):

        metadata_path = "path/metadata.json"
        cwd_path = "path/current"
        invalid_coexist_options = ["t", "template", "template-file", "parameters-override"]

        iac_hook_wrapper_instance_mock = MagicMock()
        iac_hook_wrapper_instance_mock.prepare.return_value = metadata_path
        iac_hook_wrapper_mock.return_value = iac_hook_wrapper_instance_mock
        prompt_experimental_mock.return_value = True

        getcwd_mock.return_value = cwd_path

        path_exists_mock.return_value = False

        hook_package_id_option = HookPackageIdOption(
            param_decls=(self.name, self.opt),
            force_prepare=False,
            invalid_coexist_options=invalid_coexist_options,
        )
        ctx = MagicMock()
        opts = {
            "hook_package_id": self.terraform,
        }
        args = []
        hook_package_id_option.handle_parse_result(ctx, opts, args)
        iac_hook_wrapper_instance_mock.prepare.assert_called_once_with(
            os.path.join(cwd_path, ".aws-sam-iacs", "iacs_metadata"), cwd_path, False, None, None
        )
        self.assertEqual(opts.get("template_file"), metadata_path)

    @patch("samcli.commands._utils.custom_options.hook_package_id_option.update_experimental_context")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.prompt_experimental")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.os.getcwd")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.os.path.exists")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.IacHookWrapper")
    def test_valid_hook_package_with_use_container_and_build_image(
        self,
        iac_hook_wrapper_mock,
        path_exists_mock,
        getcwd_mock,
        prompt_experimental_mock,
        update_experimental_context_mock,
    ):

        metadata_path = "path/metadata.json"
        cwd_path = "path/current"
        invalid_coexist_options = ["t", "template", "template-file", "parameters-override"]

        iac_hook_wrapper_instance_mock = MagicMock()
        iac_hook_wrapper_instance_mock.prepare.return_value = metadata_path
        iac_hook_wrapper_mock.return_value = iac_hook_wrapper_instance_mock
        prompt_experimental_mock.return_value = True

        getcwd_mock.return_value = cwd_path

        path_exists_mock.return_value = False

        hook_package_id_option = HookPackageIdOption(
            param_decls=(self.name, self.opt),
            force_prepare=False,
            invalid_coexist_options=invalid_coexist_options,
        )
        ctx = MagicMock()
        ctx.command.name = "build"
        opts = {
            "hook_package_id": self.terraform,
            "use_container": True,
            "build_image": "image",
        }
        args = []
        hook_package_id_option.handle_parse_result(ctx, opts, args)
        iac_hook_wrapper_instance_mock.prepare.assert_called_once_with(
            os.path.join(cwd_path, ".aws-sam-iacs", "iacs_metadata"), cwd_path, False, None, None
        )
        self.assertEqual(opts.get("template_file"), metadata_path)

    @patch("samcli.commands._utils.custom_options.hook_package_id_option.update_experimental_context")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.prompt_experimental")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.os.getcwd")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.os.path.exists")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.IacHookWrapper")
    def test_invalid_hook_package_with_use_container_and_no_build_image(
        self,
        iac_hook_wrapper_mock,
        path_exists_mock,
        getcwd_mock,
        prompt_experimental_mock,
        update_experimental_context_mock,
    ):

        metadata_path = "path/metadata.json"
        cwd_path = "path/current"
        invalid_coexist_options = ["t", "template", "template-file", "parameters-override"]

        iac_hook_wrapper_instance_mock = MagicMock()
        iac_hook_wrapper_instance_mock.prepare.return_value = metadata_path
        iac_hook_wrapper_mock.return_value = iac_hook_wrapper_instance_mock
        prompt_experimental_mock.return_value = True

        getcwd_mock.return_value = cwd_path

        path_exists_mock.return_value = False

        hook_package_id_option = HookPackageIdOption(
            param_decls=(self.name, self.opt),
            force_prepare=False,
            invalid_coexist_options=invalid_coexist_options,
        )
        ctx = MagicMock()
        ctx.command.name = "build"
        opts = {
            "hook_package_id": self.terraform,
            "use_container": True,
        }
        args = []
        with self.assertRaises(
            click.UsageError,
            msg="Missing required parameter --build-image.",
        ):
            hook_package_id_option.handle_parse_result(ctx, opts, args)

    @patch("samcli.commands._utils.custom_options.hook_package_id_option.update_experimental_context")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.prompt_experimental")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.os.getcwd")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.os.path.exists")
    @patch("samcli.commands._utils.custom_options.hook_package_id_option.IacHookWrapper")
    def test_valid_hook_package_with_use_container_false_and_no_build_image(
        self,
        iac_hook_wrapper_mock,
        path_exists_mock,
        getcwd_mock,
        prompt_experimental_mock,
        update_experimental_context_mock,
    ):

        metadata_path = "path/metadata.json"
        cwd_path = "path/current"
        invalid_coexist_options = ["t", "template", "template-file", "parameters-override"]

        iac_hook_wrapper_instance_mock = MagicMock()
        iac_hook_wrapper_instance_mock.prepare.return_value = metadata_path
        iac_hook_wrapper_mock.return_value = iac_hook_wrapper_instance_mock
        prompt_experimental_mock.return_value = True

        getcwd_mock.return_value = cwd_path

        path_exists_mock.return_value = False

        hook_package_id_option = HookPackageIdOption(
            param_decls=(self.name, self.opt),
            force_prepare=False,
            invalid_coexist_options=invalid_coexist_options,
        )
        ctx = MagicMock()
        ctx.command.name = "build"
        opts = {
            "hook_package_id": self.terraform,
            "use_container": False,
        }
        args = []
        hook_package_id_option.handle_parse_result(ctx, opts, args)
        iac_hook_wrapper_instance_mock.prepare.assert_called_once_with(
            os.path.join(cwd_path, ".aws-sam-iacs", "iacs_metadata"), cwd_path, False, None, None
        )
        self.assertEqual(opts.get("template_file"), metadata_path)
