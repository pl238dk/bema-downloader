from glob import glob
import re
import string
import requests
requests.packages.urllib3.disable_warnings()

print('[I] Welcome to BEMA :)')

base_url = 'https://www.bemadiscipleship.com'
#safe_filename_chars = [' ', '.', '_']
safe_filename_chars = string.ascii_letters + string.digits + ' ._-'

def get_local_episodes():
	print('[I] Checking for existing downloads')
	output = {
		'files': [],
		'max':	0,
		'missing': [],
	}
	output['files'] = glob('files/*.mp3')
	print(f'[I] Found {len(output["files"])} files')
	if not output['files']:
		return output
	episode_numbers = [x.split(' ')[1] for x in output['files'] if x]
	output['max'] = int(max(episode_numbers))
	max_range = [f'{x}'.zfill(3) for x in range(output['max'])]
	output['missing'] = list(set(max_range) - set(episode_numbers))
	return output

def get_episode(number):
	global safe_filename_chars
	global base_url
	response = requests.get(f'{base_url}/{number}', verify=False)
	text = response.text
	# episode number
	re_string = '<h5>Episode ([0-9]{1,3})</h5>'
	episode_number = re.findall(re_string, text)
	if len(episode_number) > 0:
		episode_number = episode_number[0].zfill(3)
	# episode URL
	re_string = 'https://aphid\.fireside\.fm/d/[0-9]+/[a-f0-9\-]+/[a-f0-9\-]+\.mp3'
	episode_url = re.findall(re_string, text)
	if len(episode_url) > 0:
		episode_url = episode_url[0]
	# episode name
	re_string = '<h1>(.+)</h1>'
	episode_name = re.findall(re_string, text)
	if len(episode_name) > 0:
		episode_name = episode_name[0]
	episode_name_safe = ''.join(x if x in safe_filename_chars else '_' for x in episode_name).rstrip()
	#episode_name_safe = ''.join([x for x in episode_name if re.match(r'\w', x)])
	
	# download large file
	filename = f'Episode {episode_number} - {episode_name_safe}.mp3'
	with requests.get(episode_url, verify=False) as r:
		r.raise_for_status()
		with open(f'files/{filename}', 'wb') as f:
			for chunk in r.iter_content(chunk_size=8192):
				f.write(chunk)
			print(f'[I] Writing episode to {filename}')
	return

def get_episode_content(content):
	global safe_filename_chars
	text = content.text
	# episode number
	re_string = '<h5>Episode ([0-9]{1,3})</h5>'
	episode_number = re.findall(re_string, text)
	if len(episode_number) > 0:
		episode_number = episode_number[0].zfill(3)
	# episode URL
	re_string = 'https://aphid\.fireside\.fm/d/[0-9]+/[a-f0-9\-]+/[a-f0-9\-]+\.mp3'
	episode_url = re.findall(re_string, text)
	if len(episode_url) > 0:
		episode_url = episode_url[0]
	# episode name
	re_string = '<h1>(.+)</h1>'
	episode_name = re.findall(re_string, text)
	if len(episode_name) > 0:
		episode_name = episode_name[0]
	episode_name_safe = ''.join(x if x in safe_filename_chars else '_' for x in episode_name).rstrip()
	#episode_name_safe = ''.join([x for x in episode_name if re.match(r'\w', x)])
	
	# download large file
	filename = f'Episode {episode_number} - {episode_name_safe}.mp3'
	with requests.get(episode_url, verify=False) as r:
		r.raise_for_status()
		with open(f'files/{filename}', 'wb') as f:
			for chunk in r.iter_content(chunk_size=8192):
				f.write(chunk)
			print(f'[I] Writing episode to {filename}')
	return

def get_new_episodes(last_episode_number):
	global base_url
	print(f'[I] Checking for episodes after #{last_episode_number}')
	new_episode_number = last_episode_number + 1
	response = requests.get(f'{base_url}/{new_episode_number}', verify=False)
	while response.status_code == 200:
		print(f'[W] Missing new episode {new_episode_number}.. grabbing')
		get_episode_content(response)
		new_episode_number += 1
		response = requests.get(f'{base_url}/{new_episode_number}', verify=False)
	print('[I] No more new episodes :)')
	return

# find which files have already been downloaded

o = get_local_episodes()
if not o['files']:
	print('[W] No episodes found in ./files.. grabbing')
	episode_number = 0
	response = requests.get(f'{base_url}/{episode_number}', verify=False)
	get_episode_content(response)
	get_new_episodes(episode_number)
elif o['missing']:
	print(f'[W] Missing episodes: {o["missing"]}.. grabbing')
	for episode in o['missing']:
		get_episode(int(episode))
	get_new_episodes(o['max'])
else:
	print('[I] No missing episodes!')
	get_new_episodes(o['max'])

print('[I] End')