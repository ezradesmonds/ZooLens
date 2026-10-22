<?php

namespace App\Http\Controllers;

use App\Http\Requests\ScanRequest;

class ScanController extends Controller
{
    public function store(ScanRequest $request)
    {
        // MOCK: bukan hasil inferensi model. Gambar divalidasi tapi tidak disimpan.
        // Diganti ScanService + FastAPI di Week 5-7.
        return response()->json([
            'status' => 'success',
            'mock' => true,
            'image' => ['width' => 1280, 'height' => 960],
            'detections' => [
                [
                    'class_id' => 3,
                    'confidence' => 0.91,
                    'bbox' => [100, 80, 300, 260],
                    'animal' => null,
                    'is_new_discovery' => false,
                    'badge' => null,
                ],
            ],
            'progress' => ['collected' => 0, 'total' => 5, 'percentage' => 0],
        ]);
    }
}