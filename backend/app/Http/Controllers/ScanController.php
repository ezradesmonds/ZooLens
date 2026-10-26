<?php

namespace App\Http\Controllers;

use App\Http\Requests\ScanRequest;
use App\Services\FactsheetService;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class ScanController extends Controller
{
    public function store(ScanRequest $request, FactsheetService $factsheets)
    {
        $file = $request->file('image');
        $aiServiceUrl = config('services.ai.url', 'http://127.0.0.1:8001');

        $isMock = false;
        try {
            $response = Http::timeout(10)
                ->attach('file', file_get_contents($file->getRealPath()), $file->getClientOriginalName())
                ->post($aiServiceUrl . '/predict');

            if ($response->successful()) {
                $aiResult = $response->json();
            } else {
                throw new \Exception('AI service returned HTTP ' . $response->status());
            }
        } catch (\Throwable $e) {
            Log::warning('FastAPI connection failed, falling back to mock: ' . $e->getMessage());
            $isMock = true;
            $aiResult = [
                'image_width' => 1280,
                'image_height' => 960,
                'detections' => [
                    ['class_id' => 3, 'confidence' => 0.91, 'bbox' => [100, 80, 300, 260]],
                ],
            ];
        }

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
            'mock' => $isMock,
            'image' => [
                'width' => $aiResult['image_width'],
                'height' => $aiResult['image_height'],
            ],
            'detections' => $detections,
            'progress' => ['collected' => 0, 'total' => 5, 'percentage' => 0],
        ]);
    }
}