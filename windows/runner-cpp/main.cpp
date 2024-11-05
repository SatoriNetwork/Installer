#include <iostream>
#include <fstream>
#include <filesystem>
#include <windows.h>
#include <string>
#include <shlobj.h>
#include <shobjidl.h>
#include <locale>
#include <codecvt>

// Conversion function from wide string to narrow string
std::string wstringToString(const std::wstring& wstr) {
    std::wstring_convert<std::codecvt_utf8<wchar_t>, wchar_t> converter;
    return converter.to_bytes(wstr);
}

void createDesktopShortcut(const std::wstring& targetPath, const std::wstring& shortcutPath, const std::wstring& description) {
    HRESULT hres;
    CoInitialize(NULL);

    // Get a pointer to the IShellLink interface.
    IShellLink* psl = nullptr;
    hres = CoCreateInstance(CLSID_ShellLink, NULL, CLSCTX_INPROC_SERVER, IID_IShellLink, (void**)&psl);
    if (SUCCEEDED(hres)) {
        // Set the path to the executable and description
        psl->SetPath(wstringToString(targetPath).c_str());
        psl->SetDescription(wstringToString(description).c_str());

        // Set the icon location to the executable itself
        psl->SetIconLocation(wstringToString(targetPath).c_str(), 0);

        // Query IShellLink for the IPersistFile interface for saving the shortcut.
        IPersistFile* ppf = nullptr;
        hres = psl->QueryInterface(IID_IPersistFile, (void**)&ppf);

        if (SUCCEEDED(hres)) {
            // Save the shortcut. Use IPersistFile::Save to save the .lnk file.
            hres = ppf->Save(shortcutPath.c_str(), TRUE);
            ppf->Release();
        }
        psl->Release();
    }

    CoUninitialize();
}

int main() {
    try {
        // Get AppData path
        wchar_t appdata[MAX_PATH];
        if (!GetEnvironmentVariableW(L"APPDATA", appdata, MAX_PATH)) {
            throw std::runtime_error("Failed to get APPDATA environment variable");
        }
        std::filesystem::path satoriPath = std::filesystem::path(appdata) / L"Satori";

        // Create required folders (only creates if they don't already exist)
        std::cout << "Creating Satori folders...\n";
        std::vector<std::string> folders = {"config", "data", "models", "wallet"};
        for (const auto& folder : folders) {
            std::filesystem::create_directories(satoriPath / folder);
        }

        // Get the current executable path
        wchar_t exePath[MAX_PATH];
        if (!GetModuleFileNameW(NULL, exePath, MAX_PATH)) {
            throw std::runtime_error("Failed to get current executable path");
        }

        // Copy the executable to the satoriPath directory (attempt every time)
        std::filesystem::path targetExePath = satoriPath / L"Satori.exe";
        try {
            std::cout << "Attempting to copy executable to Satori folder...\n";
            std::filesystem::copy_file(exePath, targetExePath, std::filesystem::copy_options::overwrite_existing);
            std::cout << "Executable copied successfully.\n";
        } catch (const std::filesystem::filesystem_error& e) {
            std::cerr << "Failed to copy executable. It might be in use. Skipping update. Error: " << e.what() << std::endl;
        }

        // Create startup batch file
        std::cout << "Creating startup script...\n";
        auto startupPath = std::filesystem::path(appdata) /
                          L"Microsoft/Windows/Start Menu/Programs/Startup/satori.bat";

        std::ofstream batch(startupPath);
        if (!batch) {
            throw std::runtime_error("Failed to create batch file");
        }

        batch << "@echo off\n"
              << "title Satori Neuron\n"
              << ":restart\n"
              << "start \"docker\" \"C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe\"\n"
              << ":wait_for_docker\n"
              << "docker info >nul 2>&1\n"
              << "if %ERRORLEVEL% neq 0 (\n"
              << "    timeout /T 5 > NUL\n"
              << "    echo Waiting for Docker to start ...\n"
              << "    goto wait_for_docker\n"
              << ")\n"
              << "docker stop satorineuron >nul 2>&1\n"
              << "docker pull satorinet/satorineuron:latest\n"
              << "start http://localhost:24601\n"
              << "docker run --rm -it --name satorineuron -p 24601:24601 -v \"%APPDATA%\\Satori\\wallet:/Satori/Neuron/wallet\" -v \"%APPDATA%\\Satori\\config:/Satori/Neuron/config\" -v \"%APPDATA%\\Satori\\data:/Satori/Neuron/data\" -v \"%APPDATA%\\Satori\\models:/Satori/Neuron/models\" --env ENV=prod satorinet/satorineuron:latest ./start.sh\n"
              << "echo.\n"
              << "if %ERRORLEVEL% EQU 0 (\n"
              << "    echo Container shutting down\n"
              << "    exit\n"
              << ") else if %ERRORLEVEL% EQU 1 (\n"
              << "    echo Restarting and updating Container\n"
              << "    goto restart\n"
              << ") else if %ERRORLEVEL% EQU 2 (\n"
              << "    REM this should never be seen as it is intercepted by app.py and handled to just restart satori within the container\n"
              << "    echo Restarting and updating Container\n"
              << "    goto restart\n"
              << ") else if %ERRORLEVEL% EQU 125 (\n"
              << "    echo Docker daemon error - possibly shutdown\n"
              << "    pause\n"
              << ") else if %ERRORLEVEL% EQU 137 (\n"
              << "    echo Container was killed - possibly out of memory\n"
              << "    pause\n"
              << ") else if %ERRORLEVEL% EQU 126 (\n"
              << "    echo Command cannot be invoked\n"
              << "    pause\n"
              << ") else if %ERRORLEVEL% EQU 127 (\n"
              << "    echo Command not found\n"
              << "    pause\n"
              << ") else if %ERRORLEVEL% EQU 130 (\n"
              << "    echo Container was terminated by Ctrl+C\n"
              << "    pause\n"
              << ") else if %ERRORLEVEL% EQU 143 (\n"
              << "    echo Container received shutdown request\n"
              << "    pause\n"
              << ") else (\n"
              << "    echo Unknown error code: %ERRORLEVEL%\n"
              << "    pause\n"
              << ")\n"
              << "\n";

        batch.close();

        // Launch the batch file
        std::cout << "Starting Satori...\n";
        ShellExecuteW(NULL, L"open", startupPath.c_str(), NULL, NULL, SW_SHOWNORMAL);

        // Create Desktop Shortcut if it doesn't already exist
        wchar_t desktopPath[MAX_PATH];
        if (SHGetFolderPathW(NULL, CSIDL_DESKTOP, NULL, 0, desktopPath) != S_OK) {
            throw std::runtime_error("Failed to get Desktop folder path");
        }

        std::wstring shortcutPath = std::wstring(desktopPath) + L"\\Satori.lnk";
        if (!std::filesystem::exists(shortcutPath)) {
            std::cout << "Creating desktop shortcut...\n";
            createDesktopShortcut(targetExePath, shortcutPath, L"Satori Neuron");
        } else {
            std::cout << "Desktop shortcut already exists. Skipping creation.\n";
        }

        std::cout << "Setup completed successfully!\n";
        return 0;

    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        std::cout << "Press Enter to exit...";
        std::cin.get();
        return 1;
    }
}
