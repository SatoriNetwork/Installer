#include <iostream>
#include <fstream>
#include <filesystem>
#include <windows.h>
#include <string>

int main() {
    try {
        // Get AppData path
        char* appdata = nullptr;
        size_t len;
        _dupenv_s(&appdata, &len, "APPDATA");
        std::filesystem::path satoriPath = std::filesystem::path(appdata) / "Satori";
        free(appdata);

        // Create required folders
        std::cout << "Creating Satori folders...\n";
        std::vector<std::string> folders = {"config", "data", "models", "wallet"};
        for (const auto& folder : folders) {
            std::filesystem::create_directories(satoriPath / folder);
        }

        // Create startup batch file
        std::cout << "Creating startup script...\n";
        auto startupPath = std::filesystem::path(getenv("APPDATA")) /
                          "Microsoft/Windows/Start Menu/Programs/Startup/satori.bat";

        std::ofstream batch(startupPath);
        if (!batch) {
            throw std::runtime_error("Failed to create batch file");
        }

        batch << "@echo off\n"
              << "title Satori Neuron\n"
              << ":start_docker\n"
              << "start \"docker\" \"C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe\"\n"
              << "REM Wait for Docker Desktop to fully start\n"
              << "timeout /T 30 /nobreak > NUL\n"
              << "REM Pull the latest Docker image\n"
              << "docker pull satorinet/satorineuron:latest\n"
              << "timeout /T 10 /nobreak > NUL\n"
              << "REM Run the Docker container\n"
              << "docker run --rm -it --name satorineuron -p 24601:24601"
              << " -v %APPDATA%\\Satori\\wallet:/Satori/Neuron/wallet"
              << " -v %APPDATA%\\Satori\\config:/Satori/Neuron/config"
              << " -v %APPDATA%\\Satori\\data:/Satori/Neuron/data"
              << " -v %APPDATA%\\Satori\\models:/Satori/Neuron/models"
              << " --env ENV=prod satorinet/satorineuron:latest ./start.sh\n"
              << "REM Infinite loop to check the endpoint\n"
              << ":check_loop\n"
              << "echo Checking health endpoint...\n"
              << "timeout /T 30 > NUL  REM Wait for 30 seconds before checking\n"
              << "\n"
              << "REM ask the server what version we should use\n"
              << "curl --silent --fail https://stage.satorinet.io/version/neuron -o %APPDATA%\\Satori\\config\\versions.json\n"
              << "if %ERRORLEVEL% neq 0 (\n"
              << "    echo .\n"
              << ") else (\n"
              << "    REM Extract the neuron and image versions from the JSON response\n"
              << "    for /f \"tokens=2 delims=:,}\" %%a in ('findstr \"neuron\" %APPDATA%\\Satori\\config\\versions.json') do set latest_version_neuron=%%~a\n"
              << "    for /f \"tokens=2 delims=:,}\" %%a in ('findstr \"image\" %APPDATA%\\Satori\\config\\versions.json') do set latest_version_image=%%~a\n"
              << "\n"
              << "    REM Remove any extra characters like quotes or whitespace from versions\n"
              << "    set latest_version_neuron=%latest_version_neuron:~1%\n"
              << "    set latest_version_image=%latest_version_image:~1%\n"
              << "\n"
              << "    REM Extract the current versions from the version.yaml file\n"
              << "    for /f \"tokens=2 delims=: \" %%a in ('findstr \"version:\" %APPDATA%\\Satori\\config\\version.yaml') do set current_version=%%a\n"
              << "\n"
              << "    REM Remove any leading/trailing whitespace from current_version\n"
              << "    for /f \"delims= \" %%a in (\"%current_version%\") do set current_version=%%a\n"
              << "\n"
              << "    REM Split versions to compare major and minor numbers only\n"
              << "    for /f \"tokens=1,2 delims=.\" %%a in (\"%current_version%\") do set current_major_minor=%%a.%%b\n"
              << "    for /f \"tokens=1,2 delims=.\" %%a in (\"%latest_version_neuron%\") do set latest_major_minor_neuron=%%a.%%b\n"
              << "    for /f \"tokens=1,2 delims=.\" %%a in (\"%latest_version_image%\") do set latest_major_minor_image=%%a.%%b\n"
              << "\n"
              << "    REM Compare the neuron version (if major or minor changed, update code)\n"
              << "    if \"%latest_major_minor_neuron%\" neq \"%current_major_minor%\" (\n"
              << "        echo Neuron update required. Latest neuron version: %latest_version_neuron%, Current version: %current_version%\n"
              << "        echo Notifying localhost server for neuron update...\n"
              << "        curl --silent --fail https://localhost:24601/update/code > NUL\n"
              << "\n"
              << "        REM If the above call fails, handle failure appropriately\n"
              << "        if %ERRORLEVEL% neq 0 (\n"
              << "            echo Failed to notify localhost server for neuron update.\n"
              << "        ) else (\n"
              << "            echo Neuron update notification succeeded.\n"
              << "        )\n"
              << "    ) else (\n"
              << "        echo No neuron update required. Latest neuron version: %latest_version_neuron%.\n"
              << "    )\n"
              << "\n"
              << "    REM Compare the image version (if major or minor changed, restart Docker)\n"
              << "    if \"%latest_major_minor_image%\" neq \"%current_major_minor%\" (\n"
              << "        echo Image update required. Latest image version: %latest_version_image%, Current version: %current_version%\n"
              << "        echo Restarting the Docker process to pull the latest image...\n"
              << "        REM attempt to stop neuron incase it is already running\n"
              << "        docker stop satorineuron\n"
              << "        goto start_docker\n"
              << "    ) else (\n"
              << "        echo No image update required. Latest image version: %latest_version_image%.\n"
              << "    )\n"
              << ")\n";

        batch.close();

        // Launch the batch file
        std::cout << "Starting Satori...\n";
        ShellExecute(NULL, "open", startupPath.string().c_str(),
                    NULL, NULL, SW_SHOWNORMAL);

        // std::cout << "Satori started successfully!\n";
        // std::cout << "Press Enter to exit...";
        // std::cin.get();

        return 0;

    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        std::cout << "Press Enter to exit...";
        std::cin.get();
        return 1;
    }
}
