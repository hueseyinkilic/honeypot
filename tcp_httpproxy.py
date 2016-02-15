#!/usr/bin/env python2
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import re, testrun, traceback, uuid
from utils import TextChannel, readline

def make_tcp_httpproxy_handler(tcp_handler):
	def handle_tcp_httpproxy(origsocket, dstport):
		socket = TextChannel(origsocket)

		try:
			target = readline(socket).strip()
			rematch = re.match("CONNECT [^:]+(:[0-9]+)? ?.*", target)

			if not rematch:
				raise Exception('Unexpected request')

			port_num = int(rematch.groups(":80")[0][1:])

			# Skip headers
			while readline(socket).strip() != '':
				pass

			socket.send("HTTP/1.0 200 Connection established\nProxy-agent: Netscape-Proxy/1.1\n\n")
			print("Forwarding intruder to fake port {}/tcp".format(port_num))

		except Exception as err:
			#print(traceback.format_exc())
			socket.close()
			return

		tcp_handler(origsocket, port_num)

	return handle_tcp_httpproxy

if __name__ == "__main__":
	def dummy_tcp_handler(socket, dstport):
		TextChannel(socket).send("Request for port {}/tcp\n".format(dstport))
		socket.close()
	testrun.run(8118, 8118, make_tcp_httpproxy_handler(dummy_tcp_handler))
