<?php

namespace App\Http\Controllers;

use App\Http\Requests\ScanRequest;
use App\Services\FactsheetService;

class ScanController extends Controller
{
    public function store(ScanRequest $request, FactsheetService $factsheets)
    {
        // MOCK: bukan hasil inferensi model. Diganti panggilan FastAPI di Week 7.
        $aiResult = [
            'image_width' => 1280,
            'image_height' => 960,
            'detections' => [
                ['class_id' => 3, 'confidence' => 0.91, 'bbox' => [100, 80, 300, 260]],
            ],
        ];

        $detections = [];

        foreach ($aiResult['detections'] as $detection) {
            $animal = $factsheets->findByClassId($detection['class_id']);

            if ($animal === null) {
                continue;
            }

            $detections[] = [
                'class_id' => $detection['class_id'],
                'confidence' => $detection['confidence'],
                'bbox' => $detection['bbox'],
                'animal' => $factsheets->format($animal),
                'is_new_discovery' => false, // diisi di Week 6
                'badge' => null,             // diisi di Week 6
            ];
        }

        if ($detections === []) {
            return response()->json([
                'status' => 'error',
                'code' => 'unknown_class',
                'message' => 'Satwa tidak dikenali.',
            ]);
        }

        return response()->json([
            'status' => 'success',
            'mock' => true,
            'image' => [
                'width' => $aiResult['image_width'],
                'height' => $aiResult['image_height'],
            ],
            'detections' => $detections,
            'progress' => ['collected' => 0, 'total' => 5, 'percentage' => 0],
        ]);
    }
}