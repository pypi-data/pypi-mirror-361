#ifndef IIC_GUARD_H
#define IIC_GUARD_H

#include <stdint.h>

// Represents a handle to an opened I2C device.
// The implementation is hidden from the user.
typedef struct iic_device iic_device_t;

/**
 * @brief Opens an I2C bus and initializes a device at a specific address.
 *
 * @param bus_path The path to the I2C bus (e.g., "/dev/i2c-1").
 * @param device_addr The 7-bit address of the I2C device.
 * @param[out] dev_handle Pointer to a variable that will receive the device handle.
 * @return 0 on success, or a standard C errno value on failure.
 */
int iic_open(const char* bus_path, uint8_t device_addr, iic_device_t** dev_handle);

/**
 * @brief Closes an I2C device and frees associated resources.
 *
 * @param dev The device handle to close.
 */
void iic_close(iic_device_t* dev);

/**
 * @brief Reads a single byte from a specific register of an I2C device.
 *
 * @param dev The device handle.
 * @param reg_addr The address of the register to read from.
 * @param[out] value Pointer to store the read value.
 * @return 0 on success, -1 on failure.
 */
int iic_read_register(iic_device_t* dev, uint8_t reg_addr, uint8_t* value);

/**
 * @brief Writes a single byte to a specific register of an I2C device.
 *
 * @param dev The device handle.
 * @param reg_addr The address of the register to write to.
 * @param value The byte value to write.
 * @return 0 on success, -1 on failure.
 */
int iic_write_register(iic_device_t* dev, uint8_t reg_addr, uint8_t value);

#endif // IIC_GUARD_H 