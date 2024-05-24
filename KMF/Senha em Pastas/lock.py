import win32security
import ntsecuritycon as con
from os import listdir, path, getlogin


def set_folder_permissions(folder_path, sid, permission_type):
    folder_security_descriptor = win32security.GetFileSecurity(
        folder_path, win32security.DACL_SECURITY_INFORMATION
    )

    dacl = folder_security_descriptor.GetSecurityDescriptorDacl()

    if permission_type == 'deny':
        access_mask = con.FILE_ALL_ACCESS
        dacl.AddAccessDeniedAce(win32security.ACL_REVISION, access_mask, sid)
    elif permission_type == 'allow':
        access_mask = con.FILE_ALL_ACCESS
        dacl.AddAccessAllowedAce(win32security.ACL_REVISION, access_mask, sid)

    folder_security_descriptor.SetSecurityDescriptorDacl(1, dacl, 0)
    win32security.SetFileSecurity(folder_path, win32security.DACL_SECURITY_INFORMATION, folder_security_descriptor)

def lock_folder(folder_path, username):
    sid, domain, type = win32security.LookupAccountName(None, username)
    set_folder_permissions(folder_path, sid, "deny")


for folder in [file for file in listdir() if path.isdir(file)]:
    lock_folder(folder, getlogin())
