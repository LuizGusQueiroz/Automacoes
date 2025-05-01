from os import listdir, path, getlogin
import ntsecuritycon as con
import win32security


def set_folder_permissions(folder_path, sid, permission_type):
    folder_security_descriptor = win32security.GetFileSecurity(
        folder_path, win32security.DACL_SECURITY_INFORMATION
    )

    dacl = folder_security_descriptor.GetSecurityDescriptorDacl()
    if permission_type == 'deny':
        dacl.AddAccessDeniedAce(win32security.ACL_REVISION, con.FILE_ALL_ACCESS, sid)
    elif permission_type == 'allow':
        # Remover qualquer ACE de negação existente antes de adicionar a de permissão
        for i in range(dacl.GetAceCount()):
            ace = dacl.GetAce(i)
            if ace[2] == sid and ace[1] & con.FILE_ALL_ACCESS:
                dacl.DeleteAce(i)
                break
        dacl.AddAccessAllowedAce(win32security.ACL_REVISION, con.FILE_ALL_ACCESS, sid)

    folder_security_descriptor.SetSecurityDescriptorDacl(1, dacl, 0)
    win32security.SetFileSecurity(folder_path, win32security.DACL_SECURITY_INFORMATION, folder_security_descriptor)


def lock_folder(folder_path):
    sid = win32security.ConvertStringSidToSid("S-1-1-0")  # SID para o grupo "Everyone"
    set_folder_permissions(folder_path, sid, "deny")


def unlock_folder(folder_path, username):
    sid, domain, type = win32security.LookupAccountName(None, username)
    set_folder_permissions(folder_path, sid, "allow")


# Desbloqueia todas as pastas no diretório.
for file in listdir():
    if path.isdir(file):
        unlock_folder(file, getlogin())