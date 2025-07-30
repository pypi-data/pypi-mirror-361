#include "iic_guard.h"

#include <fcntl.h>      // For O_RDWR
#include <unistd.h>     // For open, close, read, write
#include <sys/ioctl.h>  // For ioctl
#include <linux/i2c-dev.h> // For I2C_SLAVE
#include <stdlib.h>     // For malloc, free
#include <stdio.h>      // For perror
#include <errno.h>      // For errno

// Opaque struct defined in the C file.
struct iic_device {
    int fd;
};

int iic_open(const char* bus_path, uint8_t device_addr, iic_device_t** dev_handle) {
    *dev_handle = NULL;
    int fd = open(bus_path, O_RDWR);
    if (fd < 0) {
        return errno;
    }

    if (ioctl(fd, I2C_SLAVE, device_addr) < 0) {
        int err = errno;
        close(fd);
        return err;
    }

    iic_device_t* dev = malloc(sizeof(iic_device_t));
    if (!dev) {
        int err = ENOMEM;
        close(fd);
        return err;
    }

    dev->fd = fd;
    *dev_handle = dev;
    return 0; // Success
}

void iic_close(iic_device_t* dev) {
    if (dev) {
        if (dev->fd >= 0) {
            close(dev->fd);
        }
        free(dev);
    }
}

int iic_read_register(iic_device_t* dev, uint8_t reg_addr, uint8_t* value) {
    if (!dev || !value) return -1;
    
    // Write the register address we want to read from
    if (write(dev->fd, &reg_addr, 1) != 1) {
        perror("Failed to write register address for reading");
        return -1;
    }

    // Read the value from that register
    if (read(dev->fd, value, 1) != 1) {
        perror("Failed to read from I2C device");
        return -1;
    }

    return 0;
}

int iic_write_register(iic_device_t* dev, uint8_t reg_addr, uint8_t value) {
    if (!dev) return -1;
    
    uint8_t buffer[2];
    buffer[0] = reg_addr;
    buffer[1] = value;

    if (write(dev->fd, buffer, 2) != 2) {
        perror("Failed to write to I2C device");
        return -1;
    }

    return 0;
} 