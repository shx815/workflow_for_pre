import Foundation
import Vision
import ImageIO

// Local OCR: never uploads note images. The caller persists JSON and Markdown.
var records: [[String: Any]] = []
for filename in CommandLine.arguments.dropFirst() {
    do {
        let request = VNRecognizeTextRequest()
        request.recognitionLevel = .accurate
        request.recognitionLanguages = ["zh-Hans", "en-US"]
        request.usesLanguageCorrection = true
        let handler = VNImageRequestHandler(url: URL(fileURLWithPath: filename))
        try handler.perform([request])
        let lines = (request.results ?? []).compactMap { observation -> [String: Any]? in
            guard let candidate = observation.topCandidates(1).first else { return nil }
            return ["text": candidate.string, "confidence": candidate.confidence]
        }
        records.append(["path": filename, "engine": "Apple Vision", "lines": lines])
    } catch {
        records.append(["path": filename, "error": String(describing: error)])
    }
}
let data = try JSONSerialization.data(withJSONObject: records, options: [.prettyPrinted, .sortedKeys])
FileHandle.standardOutput.write(data)
