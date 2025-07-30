import anywave

# specified the port number you set when launching anywave in debug_mode
port = 59000
anywave.debug_connect(port)
# after debug_connect call, the module properties dict is set.
# to get all the properties set by anywave, use anywave.properties dict

# sending a message to anywave (would appear in debug console)
anywave.send_message('test')
# get all the data available (could be a lot of data)
channels = anywave.get_data()  # get_data() will get all the channels from the current montage for the entire file duration (so it could be a lot of data)
# print the first channel array
print(channels[0].data)
# add constraints to get_data(): here we only request data for SEEG channels.
args = {'types': ['seeg']}
channels = anywave.get_data(args)
if channels:
    print(channels[0].data)
else:
    print("no data returned")  # no SEEG channels in the current montage
# now specify two channels to get data from
args = {'channels': ['A1', 'A2']}
channels = anywave.get_data(args)
if channels:
    print(channels[0].data)  # print channel A1
else:
    print("no data returned")  # no channels named A1 or A2 in the current montage

# now getting the markers
markers = anywave.get_markers()  # no arguments = get all the markers
if markers:
    print("got", len(markers), " markers")
    markers[0].print()
else:
    print('no markers')
# add constraints to get_markers: here we request only markers named Alpha
args = {'labels': ['Alpha']}
markers = anywave.get_markers(args)
if markers:
    print("got", len(markers), " markers")
    markers[0].print()
else:
    print('no markers')  # no markers named Alpha in the current data file
# get only marker with a duration
args = {'options': ["with duration"]}
markers = anywave.get_markers(args)
if markers:
    print("got", len(markers), " markers")
    markers[0].print()
else:
    print('no markers')  # no markers with duration in the current data file

# you can also request the anywave properties later
prop = anywave.get_props()

markers = []
for i in range(0, 1010):
    m = anywave.Marker(label='test', position=i)
    markers.append(m)
anywave.send_markers(markers)
