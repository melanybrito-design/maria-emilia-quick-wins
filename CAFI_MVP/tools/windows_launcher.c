#define UNICODE
#define _UNICODE
#include <windows.h>
#include <wchar.h>

/* No shell, no console, no credentials or user input in command line. */
int WINAPI wWinMain(HINSTANCE instance, HINSTANCE previous, PWSTR arguments, int show) {
    wchar_t root[32768], python[32768], script[32768], command[65536];
    DWORD count = GetModuleFileNameW(NULL, root, 32768);
    if (!count || count >= 32768) return 1;
    wchar_t *slash = wcsrchr(root, L'\\');
    if (!slash) return 1;
    *slash = L'\0';
    if (wcslen(root) > 32000) return 1;
    swprintf(python, 32768, L"%ls\\runtime\\pythonw.exe", root);
    swprintf(script, 32768, L"%ls\\CAFI.pyw", root);
    if (GetFileAttributesW(python) == INVALID_FILE_ATTRIBUTES || GetFileAttributesW(script) == INVALID_FILE_ATTRIBUTES) {
        MessageBoxW(NULL, L"Extrae toda la carpeta del ZIP antes de abrir CAFI. Mantén CAFI.exe junto a runtime, assets y CAFI.pyw.", L"CAFI · UEES", MB_OK | MB_ICONINFORMATION);
        return 1;
    }
    swprintf(command, 65536, L"\"%ls\" \"%ls\"", python, script);
    STARTUPINFOW startup = {0};
    PROCESS_INFORMATION process = {0};
    startup.cb = sizeof(startup);
    if (!CreateProcessW(python, command, NULL, NULL, FALSE, CREATE_NO_WINDOW, NULL, root, &startup, &process)) {
        MessageBoxW(NULL, L"No se pudo abrir CAFI. Revisa que se haya extraído todo el paquete y que sea una computadora Windows de 64 bits.", L"CAFI · UEES", MB_OK | MB_ICONERROR);
        return 1;
    }
    CloseHandle(process.hThread);
    CloseHandle(process.hProcess);
    return 0;
}
