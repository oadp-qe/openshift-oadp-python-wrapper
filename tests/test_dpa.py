import os
import tempfile
import yaml

from openshift_resources.oadp.data_protection_application import DataProtectionApplication
from openshift_resources.velero.backup_storage_location import BackupStorageLocation


def create_credentials_secret(credentials_file_path):
    cmd = f"oc create secret generic cloud-credentials -n openshift-adp --from-file cloud={credentials_file_path}"
    os.system(cmd)


def create_resource_dict(template_file, r_dict):
    template_dict = yaml.safe_load(template_file)
    template_dict.update(r_dict)
    cr_dict = template_dict
    return cr_dict


def test_dpa():
    create_credentials_secret("credentials")

    dpa_dict = {"metadata": {"name": "dap-auto"},
                "spec": {"backupLocations": [{"velero": {"objectStorage": {"bucket": "oadpbucket122784"}}}]
                         }
                }

    dpa = DataProtectionApplication(
        # name and namespace are mandatory but ignored by openshift_python_wrapper resource when using yaml file
        name="test-1",
        namespace="openshift-adp",
        resource_dict=create_resource_dict(template_file=open("testdata/awss3dpa.yaml"), r_dict=dpa_dict))

    dpa.create(wait=True)

    dpa.wait_for_condition(condition="Reconciled", status="True")

    next(BackupStorageLocation.get(name="dpa-test-1", namespace="openshift-adp")) \
        .wait_for_status(status="Unavailable")

    dpa.delete()
