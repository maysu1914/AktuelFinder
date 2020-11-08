# AktuelFinder
A script based on Python that shows current campaign titles of 3 big chain of stores in Turkey. This project provides you to manage campaigns by their names. It don't give you detail about campaign contents.

## Required External Libraries
- requests
- PyPDF2
- lxml
- bs4

## Supported stores
- A101
- BİM
- ŞOK

## Features
The project has 4 main features.

### Show new campaigns
When you run the script, you'll see currently new campaigns in a list. You can approve them by entering their IDs in list to command line. Approved campaigns won't show up in the new campaigns list anymore.

![image1](https://res.cloudinary.com/djiay4zdw/image/upload/v1604840632/aktuelfinder_pic1_u836co.jpg)

### Show choosed campaigns
After you choose one or more new campaigns they will show up in the chosen campaigns list. Choose operation cannot be revoked until the campaign expired, for now.

![image2](https://res.cloudinary.com/djiay4zdw/image/upload/v1604837991/aktuelfinder_pic2_nipldz.jpg)

### Show expired campaigns
When the chosen campaigns gets expired, they will show up in the expired campaigns list. You can delete them permanently by adding ':' to beginning of IDs and entering the command line.

![image3](https://res.cloudinary.com/djiay4zdw/image/upload/v1604840587/aktuelfinder_pic3_ahbzbe.jpg)

### Command line
There is a command line to managing campaigns for user. You can enter any command as stated by splitting them with ",".

![image4](https://res.cloudinary.com/djiay4zdw/image/upload/v1604840766/aktuelfinder_pic4_zoevww.jpg)
