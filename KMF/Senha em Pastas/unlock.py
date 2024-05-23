import win32security
import ntsecuritycon as con
from os import listdir, path

logins = {
    'folder': {
        'user1': '123',
        'user2': 'abc'
        }
}

def set_folder_permissions(folder_path, sid, permission_type):
    folder_security_descriptor = win32security.GetFileSecurity(
        folder_path, win32security.DACL_SECURITY_INFORMATION
    )

    dacl = folder_security_descriptor.GetSecurityDescriptorDacl()
    if permission_type == 'deny':
        dacl.AddAccessDeniedAce(win32security.ACL_REVISION, con.FILE_ALL_ACCESS, sid)
    elif permission_type == 'allow':
        dacl.AddAccessAllowedAce(win32security.ACL_REVISION, con.FILE_ALL_ACCESS, sid)

    folder_security_descriptor.SetSecurityDescriptorDacl(1, dacl, 0)
    win32security.SetFileSecurity(folder_path, win32security.DACL_SECURITY_INFORMATION, folder_security_descriptor)


def lock_folder(folder_path):
    sid = win32security.ConvertStringSidToSid("S-1-1-0")  # SID para o grupo "Everyone"
    set_folder_permissions(folder_path, sid, "deny")


def unlock_folder(folder_path, login, password, username):
    if logins.get(folder_path, {' ': None}).get(login) == password:
        sid, domain, type = win32security.LookupAccountName(None, username)
        set_folder_permissions(folder_path, sid, "allow")
        print("Pasta desbloqueada!")
    else:
        print("Login inválido")


# Define a pasta como a primeira encontrada
for file in listdir():
    if path.isdir(file):
        # Solicita login e senha para desbloquear.
        login = input('Login: ')
        password = input('Senha: ')
        unlock_folder(file, login, password, 'Usuario')
