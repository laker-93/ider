import json


tracks = [
    {
         "track_id": 1,
         "start": 0,
         "end": 115,
         "mbid": "e6d0ddc5-472a-46a8-b92e-8e49e18429b0",
         "artist": "James Holden",
         "title": "Gone Feral",
    },
    {
         "track_id": 1,
         "start":115,
         "end": 200,
         "mbid": "e6d0ddc5-472a-46a8-b92e-8e49e18429b0",
         "artist": "James Holden",
         "title": "Gone Feral",
    },
    {
         "track_id": 1,
         "start":115,
         "end": 200,
         "mbid": "bfb8eaa4-7e35-4cec-8989-a297ae8942b2",
         "artist": "96 Back & Text Chunk",
         "title": "Virtual Resonator Dream",
    },
    {
         "track_id": 1,
         "start":200,
         "end": 290,
         "mbid": "bfb8eaa4-7e35-4cec-8989-a297ae8942b2",
         "artist": "96 Back & Text Chunk",
         "title": "Virtual Resonator Dream",
    }
]

if __name__ == '__main__':
    j = json.dumps(tracks)
    print(j)
    s = "[{\"mbid\": \"e6d0ddc5-472a-46a8-b92e-8e49e18429b0\", \"artist\": \"James Holden\", \"title\": \"Gone Feral\"}, {\"mbid\": \"bfb8eaa4-7e35-4cec-8989-a297ae8942b2\", \"artist\": \"96 Back & Text Chunk\", \"title\": \"Virtual Resonator Dream\"}]"
    d = json.loads(s)
    print(  d)