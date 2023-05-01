

def is_pico_balloon(data):
    """
    Run some tests to determine if a particular telemetry is a picoballoon or not.
    """

    if 'comment' in data:
        if 'WSPR' in data['comment']:
            return True

    if 'modulation' in data:
        if 'WSPR' in data['modulation']:
            return True

    
    return False



if __name__ == "__main__":

    test_data = [
        {'software_name': 'SondeHub APRS-IS Gateway', 'software_version': '2023.04.16', 'uploader_callsign': 'LU7AA', 'path': 'TCPIP*,qAR,LU7AA', 'time_received': '2023-05-01T01:25:57.749322Z', 'payload_callsign': 'VE3OCL-35', 'datetime': '2023-05-01T01:25:57.000000Z', 'lat': 37.86416666666667, 'lon': -100.62716666666667, 'alt': 14279.880000000001, 'comment': 'DM97QU 1C 4.5V To:127 Up:-2.62m/s V:62Km/h Sun:35 WSPR PicoBalloon http://lu7aa.org/wsprx.asp?other=ve3ocl&launch=20230414114000&SSID=35&banda=20m&balloonid=03&timeslot=0&tracker=qrplabs', 'raw': 'VE3OCL-35>APRS,TCPIP*,qAR,LU7AA:/012557h3751.85N/10037.63WO000/000/A=046850 DM97QU 1C 4.5V To:127 Up:-2.62m/s V:62Km/h Sun:35 WSPR PicoBalloon http://lu7aa.org/wsprx.asp?other=ve3ocl&launch=20230414114000&SSID=35&banda=20m&balloonid=03&timeslot=0&tracker=qrplabs', 'aprs_tocall': 'APRS', 'modulation': 'APRS'},
        {'software_name': 'SondeHub APRS-IS Gateway', 'software_version': '2023.04.16', 'uploader_callsign': 'DB0ERF-10', 'path': 'WIDE1-1,WIDE2-1,qAR,DB0ERF-10', 'time_received': '2023-05-01T01:27:00.745299Z', 'payload_callsign': 'DC2EH-6', 'datetime': '2023-05-01T01:27:00.745276Z', 'lat': 51.58833333333333, 'lon': 10.350666666666667, 'alt': 662.94, 'comment': 'www.ballon.org', 'raw': 'DC2EH-6>APT3A2,WIDE1-1,WIDE2-1,qAR,DB0ERF-10:!5135.30N/01021.04EO310/018/A=002175/www.ballon.org', 'aprs_tocall': 'APT3A2', 'modulation': 'APRS'},
        {'software_name': 'SondeHub APRS-IS Gateway', 'software_version': '2023.04.16', 'uploader_callsign': 'LU7AA', 'path': 'TCPIP*,qAR,LU7AA', 'time_received': '2023-05-01T01:27:08.941191Z', 'payload_callsign': 'VE3KCL-32', 'datetime': '2023-05-01T01:27:08.000000Z', 'lat': 51.39, 'lon': -170.28816666666665, 'alt': 12640.056, 'comment': 'AO41UJ 41C 3.6V To:49 Up:0m/s V:66Km/h Sun:47 WSPR PicoBalloon http://lu7aa.org/wsprx.asp?other=ve3kcl&launch=20221021142000&SSID=32&banda=20m&balloonid=04&timeslot=8&tracker=qrplabs', 'raw': 'VE3KCL-32>APRS,TCPIP*,qAR,LU7AA:/012708h5123.40N/17017.29WO000/000/A=041470 AO41UJ 41C 3.6V To:49 Up:0m/s V:66Km/h Sun:47 WSPR PicoBalloon http://lu7aa.org/wsprx.asp?other=ve3kcl&launch=20221021142000&SSID=32&banda=20m&balloonid=04&timeslot=8&tracker=qrplabs', 'aprs_tocall': 'APRS', 'modulation': 'APRS'},
        {'software_name': 'SondeHub APRS-IS Gateway', 'software_version': '2023.04.16', 'uploader_callsign': 'WB4ELK', 'path': 'TCPIP*,qAS,WB4ELK', 'time_received': '2023-05-01T01:28:58.630233Z', 'payload_callsign': 'K6STS-21', 'datetime': '2023-05-01T01:28:47.000000Z', 'lat': 41.104, 'lon': 121.70816666666667, 'alt': 12119.762400000001, 'comment': 'GPS:1 4.10V -3C 12120m PN01UC *0T7IKK JE64 10* 52kt K6STS WSPR Pico Balloon 141', 'raw': 'K6STS-21>APRS,TCPIP*,qAS,WB4ELK:/012847h4106.24N/12142.49EO171/235/A=039763 GPS:1 4.10V -3C 12120m PN01UC *0T7IKK JE64 10* 52kt K6STS WSPR Pico Balloon 141', 'aprs_tocall': 'APRS', 'modulation': 'APRS'}
    ]

    for data in test_data:
        print(f"Telemetry: {data}")
        print(f"Is Pico Balloon: {is_pico_balloon(data)}")