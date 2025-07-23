# piratebay-uploader

upload torrents to [thepiratebay.org](https://thepiratebay.org/index.html)



## usage

```
./piratebay_uploader.py \
    -f some.torrent -d "some description" \
    -u some_user -p some_password
```

this requires a running [tor proxy](https://www.torproject.org/), by default at
[127.0.0.1:9050](https://github.com/milahu/piratebay-uploader/blob/2b2efb1c5745b1eed7c2cc65f9461599c2103187/piratebay_uploader.py#L141)

you can store your login data at
[~/.config/piratebay_uploader/config.json](https://github.com/milahu/piratebay-uploader/blob/2b2efb1c5745b1eed7c2cc65f9461599c2103187/piratebay_uploader.py#L367),
see [example-config.json](example-config.json)

`description` can also be a
[path to a description.txt file](https://github.com/milahu/piratebay-uploader/blob/2b2efb1c5745b1eed7c2cc65f9461599c2103187/piratebay_uploader.py#L388)



## account

to use this tool, you must have a user account

see [thepiratebay.org](https://thepiratebay.org/index.html) &rarr; register

currently this works by

1. [creating an account at pirates-forum.org](https://pirates-forum.org/member.php?action=register)
2. [creating a thread](https://pirates-forum.org/newthread.php?fid=32) in [Account Issues](https://pirates-forum.org/forumdisplay.php?fid=32)
  - thread title: $your_username account issues
  - thread body: your preferred TPB username and your email address
3. waiting some days for admins to create your account
4. maybe changing your password with [TPB Account Tools](https://pirates-forum.org/misc.php?page=TPB-account-tools)
