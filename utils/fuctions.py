def get_client_ip_address(request):
    req_headers = request.META
    x_forwarded_for_value = req_headers.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for_value:
        ip_addr = x_forwarded_for_value.split(',')[-1].strip()
    else:
        ip_addr = req_headers.get('REMOTE_ADDR')
    return ip_addr

#ffmpeg -f concat -i videos.txt -c copy output.mp4
#find . -type f -name "*.mp4" | sed 's/\./file \0:/g' > file_list.txt
