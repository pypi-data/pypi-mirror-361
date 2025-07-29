from batchgenerators.utilities.file_and_folder_operations import join, maybe_mkdir_p, subdirs
from yucca.pipeline.task_conversion.utils import generate_dataset_json
from yucca.paths import yucca_raw_data
import nibabel as nib
import numpy as np
import shutil


def convert(path: str, subdir: str = "brats21/training_data"):
    # Target names
    task_name = "Task012_BraTS21_NOTEST"
    task_prefix = "BraTS21_NOTEST"

    ###OUTPUT DATA
    # Target paths
    target_base = join(yucca_raw_data, task_name)

    target_imagesTr = join(target_base, "imagesTr")
    target_labelsTr = join(target_base, "labelsTr")

    target_imagesTs = join(target_base, "imagesTs")
    target_labelsTs = join(target_base, "labelsTs")

    maybe_mkdir_p(target_imagesTr)
    maybe_mkdir_p(target_labelsTs)
    maybe_mkdir_p(target_imagesTs)
    maybe_mkdir_p(target_labelsTr)

    # INPUT DATA
    # Input path and names
    base_in = join(path, subdir)
    training_samples = subdirs(base_in, join=False)
    file_suffix = ".nii.gz"

    ###Populate Target Directory###
    for sTr in training_samples:
        src_image_file_path1 = join(base_in, sTr, sTr + "_flair" + file_suffix)
        src_image_file_path2 = join(base_in, sTr, sTr + "_t1" + file_suffix)
        src_image_file_path3 = join(base_in, sTr, sTr + "_t1ce" + file_suffix)
        src_image_file_path4 = join(base_in, sTr, sTr + "_t2" + file_suffix)
        dst_image_file_path1 = f"{target_imagesTr}/{task_prefix}_{sTr}_000.nii.gz"
        dst_image_file_path2 = f"{target_imagesTr}/{task_prefix}_{sTr}_001.nii.gz"
        dst_image_file_path3 = f"{target_imagesTr}/{task_prefix}_{sTr}_002.nii.gz"
        dst_image_file_path4 = f"{target_imagesTr}/{task_prefix}_{sTr}_003.nii.gz"

        dst_label_path = f"{target_labelsTr}/{task_prefix}_{sTr}.nii.gz"
        label = nib.load(join(base_in, sTr, sTr + "_seg" + file_suffix))
        labelarr = label.get_fdata()
        labelarr[labelarr == 4.0] = 3.0
        assert np.all(np.isin(np.unique(labelarr), np.array([0, 1, 2, 3])))
        labelnew = nib.Nifti1Image(labelarr, label.affine, label.header, dtype=np.float32)
        nib.save(labelnew, dst_label_path)

        shutil.copy2(src_image_file_path1, dst_image_file_path1)
        shutil.copy2(src_image_file_path2, dst_image_file_path2)
        shutil.copy2(src_image_file_path3, dst_image_file_path3)
        shutil.copy2(src_image_file_path4, dst_image_file_path4)

    generate_dataset_json(
        join(target_base, "dataset.json"),
        target_imagesTr,
        target_imagesTs,
        ("FLAIR", "T1", "T1CE", "T2"),
        labels={0: "background", 1: "necrotic tumor core", 2: "peritumoral edematous/invaded tissue", 3: "GD-enhancing tumor"},
        regions_in_order=[[1, 2, 3], [1, 3], [3]],
        regions_labeled=[1, 2, 3],
        dataset_name=task_name,
        license="hands off!",
        dataset_description="BraTS21",
        dataset_reference="https://www.nitrc.org/projects/msseg, https://arxiv.org/abs/2206.06694",
    )


if __name__ == "__main__":
    convert()
