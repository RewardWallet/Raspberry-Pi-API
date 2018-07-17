#include <iostream>
#include <cstring>
#include <sys/shm.h>		//Used for shared memory
#include "SharedMemory.h"
#include <thread>         // std::this_thread::sleep_for
#include <chrono>         // std::chrono::seconds

int main(int argc, char *argv[])
{
    attachSharedMemory();

    if (argc >= 2)
    {
        // Arguments passed to write to shared memory
    
        // //----- WRITE TO SHARED MEMORY -----
        memcpy(&shared_memory1->some_data[0], argv[1], sizeof(char)*10);
        shared_memory1->some_flag = 1;

        std::cout << argv[1] << " written to shared memory." << std::endl;

    } else {
        // No arguments passed, wait for memory to be written
        while(true) 
        {
            //----- READ FROM SHARED MEMORY -----
            if (shared_memory1->some_flag == 1) 
            {
                char data[sizeof(char)*10];
                memcpy(&data, &shared_memory1->some_data, sizeof(char)*10);

                // Clear the data
                memset(&shared_memory1->some_data[0], 0, sizeof(shared_memory1->some_data));
                shared_memory1->some_flag = 0;
                
                // Print output
                std::cout << data << std::endl;


                // This is where we would initialize the NFC and attach the inturrupt

                return 0;
            } else {
                std::cout << "Waiting for data...\n";
                std::this_thread::sleep_for (std::chrono::seconds(1));
            }
        }
    }

    return 0;
}