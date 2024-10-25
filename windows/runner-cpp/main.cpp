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
              << "start \"docker\" \"C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe\"\n"
              << "timeout /T 30 /nobreak > NUL\n"
              << "docker pull satorinet/satorineuron:latest\n"
              << "timeout /T 10 /nobreak > NUL\n"
              << "docker run --rm -it --name satorineuron -p 24601:24601"
              << " -v %APPDATA%\\Satori\\wallet:/Satori/Neuron/wallet"
              << " -v %APPDATA%\\Satori\\config:/Satori/Neuron/config"
              << " -v %APPDATA%\\Satori\\data:/Satori/Neuron/data"
              << " -v %APPDATA%\\Satori\\models:/Satori/Neuron/models"
              << " --env ENV=prod satorinet/satorineuron:latest ./start.sh\n";
              //<< "infinite loop look at endpoint - if response, restart docker";

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
