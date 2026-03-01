from typing import Dict


def _normalize(value: float, min_v: float, max_v: float) -> float:
    if max_v <= min_v:
        return 0.5
    clamped = max(min_v, min(value, max_v))
    return (clamped - min_v) / (max_v - min_v)


def infer_mbti(features: Dict[str, float]) -> Dict[str, object]:
    eye_ratio = features.get("eye_to_face_ratio", 0.0)
    mouth_ratio = features.get("mouth_to_face_ratio", 0.0)
    jaw_ratio = features.get("jaw_to_face_ratio", 0.0)
    nose_ratio = features.get("nose_to_face_ratio", 0.0)

    e_score = _normalize(eye_ratio + mouth_ratio, 0.20, 0.55)
    n_score = _normalize(nose_ratio + eye_ratio, 0.18, 0.50)
    t_score = _normalize(nose_ratio + jaw_ratio, 0.20, 0.60)
    j_score = _normalize(jaw_ratio, 0.18, 0.45)

    personality = (
        ("E" if e_score >= 0.5 else "I")
        + ("N" if n_score >= 0.5 else "S")
        + ("T" if t_score >= 0.5 else "F")
        + ("J" if j_score >= 0.5 else "P")
    )

    confidence = round((abs(e_score - 0.5) + abs(n_score - 0.5) + abs(t_score - 0.5) + abs(j_score - 0.5)) / 2, 3)

    return {
        "mbti_type": personality,
        "confidence": confidence,
        "scores": {
            "E_vs_I": round(e_score, 3),
            "N_vs_S": round(n_score, 3),
            "T_vs_F": round(t_score, 3),
            "J_vs_P": round(j_score, 3),
        },
        "note": "Heuristic mapping for educational/demo use only; not a psychological diagnosis.",
    }
