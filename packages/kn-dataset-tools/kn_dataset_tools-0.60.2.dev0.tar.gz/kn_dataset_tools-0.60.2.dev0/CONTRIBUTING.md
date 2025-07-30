# Volunteering help for KTISEOS NYX projects

[__Promotion and Docs__](#promotion-and-docs)<br>
[__Setting up For Development__](#setting-up-for-development)<br>
[__Contributing Code__](#contributing-code)<br>
[__Previous Builds__](#previous-builds)<br>

## Promotion And Docs

We're always looking for help with:

- Video Tutorials
- Documenting
- Feature Ideas
- Aesthetic Suggestions
- Design Discussion
- New Code

Coordinate with us by:

- Opening a topic in [discussions](https://github.com/Ktiseos-Nyx/Dataset-Tools/discussions/new/choose)
- Opening an [issue](https://github.com/Ktiseos-Nyx/Dataset-Tools/issues/new/choose)
- Connect with us live on discord!

<a href="https://discord.gg/5t2kYxt7An" target="_blank">

![A flat logo for Discord](https://img.shields.io/badge/%20Discord%20_%20_%20_%20_%20_%7C-_?style=flat-square&labelColor=rgb(65%2C69%2C191)&color=rgb(65%2C69%2C191))

</a>

## Contributing Code

### Specifications

> #### Formatting/Linting Specification
>
> ```
> editor       = Visual Studio Code
> formatting   = Ruff/Black/Better Align
> docstrings   = NumPY/Sphinx
> installation = setuptools
> testing      = pytest
> typing       = Pydantic
> ui           = QT
> ```

> #### Variable dictionary
>
> ```
> # Actions
> Delegate / Arrange / Direct / Traffic / Filter / Coordinate / Assign
> Fetch / Get / Extract / Pull / Send / Feed / Push
> Delineate / Format / Detail / Cat|Concat / Show / Join / Splice
> Diverge / Unite / Resolve / Generate / Activate
> Identify / Compare / Detect / Measure / Scan / Scrutinize
> Log / Cache / Read / Load / Capture / Populate / Save
> Test / Interpret / Poll / Interrogate / Flag / Mark / Mask / Trace
> Protect / Register / Ignore / Canonize
> Check / Validate / Normalize
> Advance / Skip / Exit / Leave / Cross / Structure / Fold

> # Conditions
>
> Raw / Upstream / Downstream / Up / Down / Low / High
> Active / Passive / Inactive / Public / Private
> Extrinsic / Intrinsic / Static / Dynamic / Valid / Invalid
> Indirect / Direct / Pending / Next
> Maybe / Local / Remote / Persistent / Relevant

> # Object
>
> File / Folder / Fragment / Component / Segment
> Header/ Content / Pattern / Target / Aspect
> State / Signal / Trigger / Level / Status / Attribute
> Location / Path / Parameter / Code / Mask
> Net / Disk

> # Between bits
>
> Is / Has / Can

> # File and Folder handling

> file_contents   = data inside the file
> file_name       = exclusively
> file_path       = the path leading up to the file, with no file name
> file_path_named = relative or absolute path including name

> empty_file_name          = a file to be created
> empty_file_name_and_path = relative or absolute path including name to be created

> folder_contents            = file names inside a folder
> folder_name                = the name of the folder
> folder_name_and_path       = relative or absolute path including name
> empty_folder_name          = a folder to be created
> empty_folder_name_and_path = relative or absolute path including name to be created

> # Key and Value handling
>
> key_name
> key_name_and_path
> empty_key_name
> empty_key_name_and_path

> value_name
> value_name_and_path
> empty_key_name
> empty_key_name_and_path
> new_key_name
>
> ```

## Setting Up For Development

These are the instructions to follow for people who want to build the app with us!

### Dev Installation
>
> ```
> pip install -e .[dev]
> ```

### Update version
>
> ```
> python -m _version
> ```
>

### Run with debug logging
>
> ```
> dataset-tools -d
> ```
>
> or
>
> ```
> python -m main --log debug
> ```

### Reinstallation
>
> ```
> pip uninstall dataset-tools
> ```

## Previous Builds

### Where we started from

Here you can see some screenshots of previous versions of the application. Look at our baby pics! 🍼

<img width="797" alt="Screenshot of the Application" src="https://github.com/user-attachments/assets/7e14c542-482d-42f4-a9ae-4305c9e2c383">

<img width="459" alt="Screenshot 2024-06-14 at 22 00 40" src="https://github.com/duskfallcrew/Dataset-Tools/assets/58930427/9dc7f859-13d5-4e75-9f21-171648b3061e">
<img width="464" alt="Screenshot 2024-06-14 at 22 09 01" src="https://github.com/duskfallcrew/Dataset-Tools/assets/58930427/dbfd0678-aff4-47f2-a23f-e7cfa14582ef">
<img width="1202" alt="Screenshot 2024-06-15 at 00 03 47" src="https://github.com/duskfallcrew/Dataset-Tools/assets/58930427/a2e1b5bb-7ffc-43e9-8002-56aa977478f6">
<img width="1198" alt="Screenshot 2024-06-15 at 00 03 55" src="https://github.com/duskfallcrew/Dataset-Tools/assets/58930427/8f948d75-96ae-4ae7-b87b-0ad8887e6745">
<img width="1678" alt="Screenshot 2024-06-15 at 00 04 16" src="https://github.com/duskfallcrew/Dataset-Tools/assets/58930427/bba4d2a7-9aaa-42f3-82f8-b866db8f0084">
<img width="1183" alt="Screenshot 2024-06-15 at 14 06 00" src="https://github.com/duskfallcrew/Dataset-Tools/assets/58930427/a513f6df-1fca-421b-ae8b-401abc7741cb">
<img width="1190" alt="Screenshot 2024-06-15 at 15 01 45" src="https://github.com/duskfallcrew/Dataset-Tools/assets/58930427/10d386f8-ae21-4672-964c-5d4ebc889275">
