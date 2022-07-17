import os
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool

import m3u8
import requests


class M3U8Downloader:
    @staticmethod
    def __get_best_video(playlists):
        best_video = None
        for playlist in playlists:
            if best_video is None or playlist.stream_info.bandwidth > best_video.stream_info.bandwidth:
                best_video = playlist
        return best_video

    @staticmethod
    def __get_file(url):
        with requests.get(url) as response:
            return bytearray(response.content)

    def download(self, url, path_to_file, file):
        cpus = cpu_count()

        m3u8_master = m3u8.load(url)
        best_video = self.__get_best_video(m3u8_master.playlists)

        m3u8_video, video = m3u8.load(best_video.uri), bytearray()
        files = m3u8_video.files
        results = ThreadPool(cpus - 1).imap(self.__get_file, files)

        for result in results:
            print(len(video)//1024//1024, 'mb')
            video.extend(result)

        try:
            os.makedirs(path_to_file)
        except FileExistsError:
            pass

        with open(f'{path_to_file}/{file}.ts', 'wb') as file:
            file.write(video)


if __name__ == '__main__':
    url = 'https://player02.getcourse.ru/player/f4714d3444c85406491bbb69444d922e/630733cd3d0aa2fd5d3af3356823208f/master.m3u8?user-cdn=integros&acc-id=0&user-id=227333572&loc-mode=ru&version=5%3A2%3A1%3A0%3A2&consumer=vod&jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyLWlkIjoyMjczMzM1NzIsImNvbnN1bWVyIjoidm9kIn0.8L7Y7dkOlLKluZyEnSs6CrsCvZUwkmDp12kyuv9w3a8'
    downloader = M3U8Downloader()
    downloader.download(url, './videos', 'video')
