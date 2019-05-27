# Agile Network Service Development - P2P Homework

This project simulates the operation of the following protocol :
  - Devices continuously collect sensor data, no piece of data can be lost
  
  - Devices have a storage capacity of next to zero (can be emulated with virtual machine settings), and so must forward collected data   periodically
  - Each array has a dedicated storage server 
  - Storage servers know each others IP address
  - Every storage server can go down for an undefined period of time, data loss must be prevented
