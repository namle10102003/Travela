<?php
header('Content-Type: text/plain; charset=utf-8');

try {
    if (!isset($_POST['message']) || empty($_POST['message'])) {
        throw new Exception('Không có tin nhắn được gửi');
    }

    chdir(__DIR__ . '/scripts');
    $pythonPath = 'C:\\Users\\Public\\anaconda3\\envs\\envchat\\python.exe';
    $pythonScript = 'chatbot_backend.py';
    $message = escapeshellarg(iconv('UTF-8', 'UTF-8//IGNORE', $_POST['message']));

    $command = "$pythonPath $pythonScript $message --web";
    $output = shell_exec($command);

    if ($output === null) {
        throw new Exception('Không thể xử lý yêu cầu');
    }

    // Tìm phần câu trả lời thực sự sau dấu "📝 Câu trả lời:"
    if (preg_match('/📝 Câu trả lời:\s*(.*?)(?:\n|$)/s', $output, $matches)) {
        echo trim($matches[1]);
    } else {
        echo trim($output);
    }

} catch (Exception $e) {
    echo $e->getMessage();
}
