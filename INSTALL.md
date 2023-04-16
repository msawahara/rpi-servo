echo "dtparam=i2c_arm=on" > /boot/config.txt
echo "i2c-dev" > /etc/modules-load.d/i2c.conf

pacman -Syu
pacman -S python-pip
pip install -r < requirements.txt
