<?php

namespace App\Http\Controllers;

use App\Http\Requests\ScanRequest;
use App\Services\CollectionService;
use App\Services\FactsheetService;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class ScanController extends Controller
{
    public function store(ScanRequest $request, FactsheetService $factsheets, CollectionService $collection)
    {
        $file = $request->file('image');
        $aiServiceUrl = config('services.ai.url', 'http://127.0.0.1:8001');

        try {
            $response = Http::timeout(10)
                ->attach('file', file_get_contents($file->getRealPath()), $file->getClientOriginalName())
                ->post($aiServiceUrl . '/predict');

            if (! $response->successful()) {
                throw new \Exception('AI service returned HTTP ' . $response->status());
            }

            $aiResult = $response->json();
        } catch (\Throwable $e) {
            Log::error('FastAPI tidak bisa dihubungi: ' . $e->getMessage());

            return response()->json([
                'status' => 'error',
                'code' => 'ai_unavailable',
                'message' => 'Error 503: backend FastAPI sedang down.',
            ], 503);
        }

        $detections = [];

        foreach ($aiResult['detections'] ?? [] as $detection) {
            $animal = $factsheets->findByClassId($detection['class_id']);

            if ($animal === null) {
                continue;
            }

            $outcome = $collection->record(
                $request->user(),
                $animal,
                $detection,
                $aiResult['image_width'],
                $aiResult['image_height']
            );

            $detections[] = [
                'class_id' => $detection['class_id'],
                'confidence' => $detection['confidence'],
                'bbox' => $detection['bbox'],
                'animal' => $factsheets->format($animal),
                'is_new_discovery' => $outcome['is_new_discovery'],
                'badge' => $outcome['badge'],
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
            'image' => [
                'width' => $aiResult['image_width'],
                'height' => $aiResult['image_height'],
            ],
            'detections' => $detections,
            'progress' => $collection->progress($request->user()),
        ]);
    }
}