<?php

return [
    'confidence_threshold' => (float) env('SCAN_CONFIDENCE_THRESHOLD', 0.5),

    // Nama bahasa Indonesia untuk tampilan (kunci = common_name huruf kecil)
    'names_id' => [
        'elephant' => 'Gajah',
        'giraffe' => 'Jerapah',
        'zebra' => 'Zebra',
        'tiger' => 'Harimau',
        'rhinoceros' => 'Badak',
    ],
];