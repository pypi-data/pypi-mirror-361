# PyHaab

**PyHaab** is a Cisco-switch inventory collector that connects over SSH,
scrapes interface/VLAN/device-tracking information, and updates a single
Excel workbook *in place*.  
It is the spiritual successor of `inventory_script.py`, repackaged as a
proper Python library with both **CLI** and **importable API**.

---

## Features

* 🔌 Connects to any IOS-based switch via **Netmiko**
* 📊 Generates or updates one `.xlsx` file per run  
  *Per-switch* tabs + a global **“Switches”** summary tab
* 🌈 Cell colouring that highlights interface state and NAC status
* ⚡ Runs either as
  * a **command-line tool** (`pyhaab …`), or
  * an **importable function** (`from pyhaab import collect`)

---

## Installation

```bash
pip install pyhaab      # or  pip install --upgrade pyhaab