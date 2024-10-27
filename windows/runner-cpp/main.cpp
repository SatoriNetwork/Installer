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
              << "\n"
              << "REM Specify the image you want to get the hash for\n"
              << "set image_name=satorinet/satorineuron:latest\n"
              << "\n"
              << "REM start Docker\n"
              << "start \"docker\" \"C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe\"\n"
              << "\n"
              << "REM Wait for Docker Desktop to fully start\n"
              << "timeout /T 60 /nobreak > NUL\n"
              // possible alternative to timeout?
              //<< ":wait_for_docker\n"
              //<< "docker info >nul 2>&1\n"
              //<< "if %ERRORLEVEL% neq 0 (\n"
              //<< "    timeout /T 5 >nul\n"
              //<< "    goto wait_for_docker\n"
              //<< ")\n"
              << "\n"
              << "REM Pull the latest Docker image\n"
              << "docker pull %image_name%\n"
              << "timeout /T 10 /nobreak > NUL\n"
              << "\n"
              << "REM Get the hash of the image by inspecting it\n"
              << "for /f \"tokens=*\" %%i in ('docker inspect --format \"{{.Id}}\" %image_name%') do set prior_image_hash=%%i\n"
              << "\n"
              << "REM Display the hash\n"
              << "echo Docker Image Hash: %prior_image_hash%\n"
              << "\n"
              << "REM Run the Docker container\n"
              << "docker run --rm -it --name satorineuron -p 24601:24601"
              << " -v %APPDATA%\\Satori\\wallet:/Satori/Neuron/wallet"
              << " -v %APPDATA%\\Satori\\config:/Satori/Neuron/config"
              << " -v %APPDATA%\\Satori\\data:/Satori/Neuron/data"
              << " -v %APPDATA%\\Satori\\models:/Satori/Neuron/models"
              << " --env ENV=prod satorinet/satorineuron:latest ./start.sh\n"
              << "\n"
              << "REM Infinite loop to check the endpoint\n"
              << ":check_loop\n"
              << "echo Checking health endpoint...\n"
              << "timeout /T 21600 > NUL  REM Wait for 6 hours before checking\n"
              << "\n"
              << "REM Pull the image to make sure we have the latest version\n"
              << "docker pull %image_name%\n"
              << "\n"
              << "REM Get the hash of the image by inspecting it\n"
              << "for /f \"tokens=*\" %%i in ('docker inspect --format \"{{.Id}}\" %image_name%') do set image_hash=%%i\n"
              << "\n"
              << "REM Compare the current hash with the latest hash\n"
              << "if \"%prior_image_hash%\" neq \"%image_hash%\" (\n"
              << "    echo Image has changed, restarting Docker container...\n"
              << "    docker stop satorineuron 2>nul\n" // cleaner logs - necessary?
              << "    goto start_docker\n"
              << "\n"
              << ") else (\n"
              << "    echo No changes in image hash. No restart required.\n"
              << ")\n"
              << "goto check_loop\n"
              << "\n";
              // we'll hit the code version endpoint inside the image itself.

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
