
<img src="https://github.com/user-attachments/assets/9a97fcf9-33cd-4bea-b124-0233c5435f90" width="150"/>  


**LiveSplat** is an algorithm for realtime Gaussian splatting using RGBD camera streams. Join our [discord](https://discord.gg/rCF5SXnc) for discussion and help.

Message from the Author
------
LiveSplat was developed as a small part of a larger proprietary VR telerobotics system. I posted a video of the Gaussian splatting component of this system on Reddit and many people expressed an interest in experimenting with it themselves. So I spun it out and called it LiveSplat and now I'm making it publicly available (see installation instructions below).  

LiveSplat should be considered alpha level. I do not have the resources to test the installation on many different machines, so let me know if the application does not run on yours (assuming your machine meets the requirements).

I've decided to keep the application closed source in order to explore potential business opportunities involving this technology. If you are a business wanting to integrate this technology, please email mark@axby.cc.  

I hope you have fun with LiveSplat!  

&mdash; Mark Liu



Requirements
------------
  - Python 3.12+
  - Windows or Ubuntu (other Linux distributions may work, but are untested)
  - x86_64 CPU
  - Nvidia graphics card
  - One or more (up to four) RGBD sensors

Ubuntu Installation
------
`pip install https://livesplat.s3.us-east-2.amazonaws.com/livesplat-0.1.0-cp312-cp312-manylinux_x86_64.whl`

Windows Installation
-----
`pip install https://livesplat.s3.us-east-2.amazonaws.com/livesplat-0.1.0-cp312-cp312-win_amd64.whl`

Running
------
To run LiveSplat, you will have to create an integration script that connects to your RGBD sensors and feeds the results to the LiveSplat viewer. This repo provides an integration script for Intel Realsense devices called [livesplat_realsense.py](https://github.com/axbycc/LiveSplat/blob/main/livesplat_realsense.py).

