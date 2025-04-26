<?php

// قائمة القنوات وروابطها
$channels = [
    'syriatv' => 'https://stream.kick.com/ivs/v1/196233775518/xJVvMPK4StGw/2025/3/19/20/40/vB8FH0lKdvXA/media/hls/1080p60/playlist.m3u8',
    'Movies1' => 'https://shls-live-enc.edgenextcdn.net/out/v1/46079e838e65490c8299f902a7731168/index_2.m3u8',
    'm2' => 'https://shls-live-enc.edgenextcdn.net/out/v1/f6d718e841f8442f8374de47f18c93a7/index_2.m3u8',
    'bein1' => 'http://beworkers30.xsturta.xyz/live/194432_.m3u8',
];

// دالة تحميل المحتوى عبر cURL
function curlGet($url) {
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    $data = curl_exec($ch);
    curl_close($ch);
    return $data;
}

// الحصول على رابط الطلب
$requestUri = $_SERVER['REQUEST_URI'];
$parsedUrl = parse_url($requestUri);
$path = trim($parsedUrl['path'], '/');
$parts = explode('/', $path);

// تحقق من الطلب إذا كان بالشكل المطلوب
if (count($parts) >= 3 && $parts[0] === 'channel') {
    $channelId = $parts[1];
    $action = $parts[2];

    if (!isset($channels[$channelId])) {
        http_response_code(404);
        echo 'Channel not found';
        exit;
    }

    $baseUrl = $channels[$channelId];

    if ($action === 'stream.m3u8') {
        $playlist = curlGet($baseUrl);
        if ($playlist === false) {
            http_response_code(502);
            echo 'Failed to fetch playlist';
            exit;
        }

        $lines = explode("\n", $playlist);
        $newPlaylist = '';
        foreach ($lines as $line) {
            $line = trim($line);
            if ($line === '' || strpos($line, '#') === 0) {
                $newPlaylist .= $line . "\n";
            } else {
                $segmentUrl = dirname($baseUrl) . '/' . $line;
                $newPlaylist .= $_SERVER['REQUEST_SCHEME'].'://'.$_SERVER['HTTP_HOST']."/channel/{$channelId}/segment?url=" . urlencode($segmentUrl) . "\n";
            }
        }

        header('Content-Type: application/vnd.apple.mpegurl');
        header('Cache-Control: no-cache');
        echo $newPlaylist;
        exit;

    } elseif ($action === 'segment') {
        if (!isset($_GET['url'])) {
            http_response_code(400);
            echo 'Missing segment URL';
            exit;
        }
        $segmentUrl = urldecode($_GET['url']);

        $segmentContent = curlGet($segmentUrl);
        if ($segmentContent === false) {
            http_response_code(502);
            echo 'Failed to fetch segment';
            exit;
        }

        header('Content-Type: video/MP2T');
        header('Cache-Control: public, max-age=3600');
        echo $segmentContent;
        exit;
    }
}

http_response_code(404);
echo 'Not Found';
?>
