

class HDRInfo:

	def __init__(self, info):
		print('Checking for HDR video data...')
		self.exists = info.color_primaries == 'bt2020'
		if self.exists:
			self.sdrmap='-vf "zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p"'
			self.__setparams(info)
			
			
	def __setparams(self, info):
		self.params = 'hdr-opt=1:repeat-headers=1:colorprim=' + info.color_primaries
		self.params = self.params + ':transfer=' + info.color_transfer + ':colormatrix=' + info.color_space + ':master-display='
		self.params = self.params + 'G(' + info.green_x.split('/')[0] + ',' + info.green_y.split('/')[0] + ')'
		self.params = self.params + 'B(' + info.blue_x.split('/')[0] + ',' + info.blue_y.split('/')[0] + ')'
		self.params = self.params + 'R(' + info.red_x.split('/')[0] + ',' + info.red_y.split('/')[0] + ')'
		self.params = self.params + 'WP(' + info.white_point_x.split('/')[0] + ',' + info.white_point_y.split('/')[0] + ')'
		self.params = self.params + 'L(' +info.max_luminance.split('/')[0] + ',' + info.min_luminance.split('/')[0] + ')'
		self.params = self.params + ':max-cll="' + info.max_content + ',' + info.max_average + '"'