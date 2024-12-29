#include <pybind11/pybind11.h>
#include <math.h>
#include <random>
#include <tuple>

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

#define VERSION_INFO "0.0.2"

typedef unsigned short ushort;

template <typename T> inline T squared(T x) {
    return x * x;
}

const float kEpsilon = 0.0001f;

bool floatEquals(float a, float b) {
    return std::abs(a - b) <= kEpsilon;
}

struct Vector2 {

public:

    float x;
    float y;

    Vector2() {
        x = y = 0;
    }

    Vector2(const float x, const float y) {                                                                            
        this->x = x;
        this->y = y;
    }

    inline float MagnitudeSqr() {
        return x * x + y * y;
    }

    inline float Magnitude() {
        return sqrt(x * x + y * y);
    }

    Vector2 operator +(const Vector2& b) {
        return Vector2(this->x + b.x, this->y + b.y);
    }

    Vector2 operator -(const Vector2& b) {
        return Vector2(this->x - b.x, this->y - b.y);
    }

    Vector2 operator *(const float s) {
        return Vector2(this->x * s, this->y * s);
    }

    Vector2 operator /(const float s) {
        return Vector2(this->x / s, this->y / s);
    }

    void Swap() {
        float tmp = x;
        x = y;
        y = tmp;
    }

    void Normalize() {
        float magn = Magnitude();
        if (magn < 1e-7f)
            return;
        this->x /= magn;
        this->y /= magn;
    }

    static Vector2 DirectionToVector(ushort dir) {
        float fDir = (dir % 16384) / 16384.0f;
        Vector2 result = Vector2(1 - fDir, fDir);
        if (dir < 16384)
        {
            result.y = -result.y;
            result.Swap();
        }
        else if (dir < 32768)
        {
            result.x = -result.x;
            result.y = -result.y;
        }
        else if (dir < 49152)
        {
            result.x = -result.x;
            result.Swap();
        }

        result.Normalize();
        return result;
    }

};

namespace Mathf {

    float Sign(float v) {
        if (v < 0.0f) {
            return -1.0f;
        }
        else if (v > 0.0f) {
            return +1.0f;
        }
        else {
            return 0.0;
        }
    }

    float STriangle(Vector2 p1, Vector2 p2, Vector2 p3)
    {
        return p1.x * (p2.y - p3.y) + p2.x * (p3.y - p1.y) + p3.x * (p1.y - p2.y);
    }

}

namespace RandomGen {

    std::mt19937 gen;

    void InitSeed(unsigned int seed) {
        gen = std::mt19937(seed);
    }

    int RandomInt(int to) {
        std::uniform_int_distribution<> distr(0, to);
        return distr(gen);
    }

    float RandomFloat01() {
        std::uniform_real_distribution<> distr(0.0, 1.0);
        return float(distr(gen));
    }

    float RandomFloatRange(float from, float to) {
        std::uniform_real_distribution<> distr(from, to);
        return float(distr(gen));
    }

    Vector2 RandQuardInCircle(float dispersion, float fRatio=0.0f, Vector2 TrajLine=Vector2(0,0)) {
        int temp = RandomInt(65536);
        Vector2 dir = Vector2::DirectionToVector(temp);
        float fRandR = dispersion * RandomFloat01();

        Vector2 output;

        if (fRatio == 0.0f)
        {
            output.x = dir.x * fRandR;
            output.y = dir.y * fRandR;
        }
        else
        {
            TrajLine.Normalize();
            output = 
                TrajLine * fRandR * dir.x * fRatio + 
                Vector2(-TrajLine.y, TrajLine.x) * fRandR * dir.y;
        }

        return output;
    }

}

struct SRect {

public:

	Vector2 v1, v2, v3, v4;


    Vector2 dir, dirPerp, center;
    float lengthAhead, lengthBack, width;

    void Init(Vector2 center, Vector2 dir, float length, float width) {
        this->center = center;
        this->dir = dir;
        this->dir.Normalize();

        dirPerp.x = -dir.y;
        dirPerp.y = dir.x;

        lengthBack = lengthAhead = length;
        this->width = width;

        Vector2 pointBack = center - dir * length;
        Vector2 pointForward = center + dir * length;

        v1 = pointBack - dirPerp * width;
        v2 = pointBack + dirPerp * width;
        v3 = pointForward + dirPerp * width;
        v4 = pointForward - dirPerp * width;
    }

    void Init(Vector2 center, Vector2 dir, float lengthAhead, float lengthBack, float width) {
        this->center = center;
        this->dir = dir;
        this->dir.Normalize();

        dirPerp.x = -dir.y;
        dirPerp.y = dir.x;

        this->lengthBack = lengthBack;
        this->lengthAhead = lengthAhead;
        this->width = width;

        Vector2 pointBack = center - dir * lengthBack;
        Vector2 pointForward = center + dir * lengthAhead;

        v1 = pointBack - dirPerp * width;
        v2 = pointBack + dirPerp * width;
        v3 = pointForward + dirPerp * width;
        v4 = pointForward - dirPerp * width;
    }

    bool IsPointInside(Vector2 point) {
        Vector2 center = Vector2((v1.x + v2.x + v3.x + v4.x) / 4, (v1.y + v2.y + v3.y + v4.y) / 4);
        short rightSign = (short)Mathf::Sign(Mathf::STriangle(v1, v2, center));

        if (rightSign == 0)
        {
            return (point - center).MagnitudeSqr() < 0.001f;
        }

        return
            Mathf::Sign(Mathf::STriangle(v1, v2, point)) == rightSign && 
            Mathf::Sign(Mathf::STriangle(v2, v3, point)) == rightSign &&
            Mathf::Sign(Mathf::STriangle(v3, v4, point)) == rightSign && 
            Mathf::Sign(Mathf::STriangle(v4, v1, point)) == rightSign;
    }

    bool IntersectsWithCircle(Vector2 circleCenter, float radius) {

        if(IsPointInside(circleCenter))
            return true;

        const Vector2 newCenter = circleCenter - center;
        const Vector2 localCoordCenter = 
            Vector2(
                newCenter.x * dir.x + newCenter.y * dir.y, 
                -newCenter.x * dir.y + newCenter.y * dir.x
            );

        float dist = 0;

        if (localCoordCenter.x < -lengthBack)
            dist += squared(localCoordCenter.x - (-lengthBack));
        else if (localCoordCenter.x > lengthAhead)
            dist += squared(localCoordCenter.x - lengthAhead);

        if (localCoordCenter.y < -width)
            dist += squared(localCoordCenter.y - (-width));
        else if(localCoordCenter.y > width)
            dist += squared(localCoordCenter.y - width);

        return dist <= squared(radius);
    }

    void Compress(float AABBCoef) {

        lengthAhead *= AABBCoef;
        lengthBack *= AABBCoef;
        width *= AABBCoef;

        Init(center, dir, lengthAhead, lengthBack, width);
    }

    static Vector2 GetCenterShift(Vector2& dir, Vector2& AABBCenter) {
        Vector2 realDirVec = dir;
        Vector2 dirPerp = Vector2(realDirVec.y, -realDirVec.x);

        return realDirVec * AABBCenter.y + dirPerp * AABBCenter.x;
    }

    static SRect GetUnitRect(Vector2& AABBHalfSize, Vector2& AABBCenter, Vector2& dir)
    {
        float length = AABBHalfSize.x;
        float width = AABBHalfSize.y;

        SRect rect = SRect();
        rect.Init(AABBCenter + GetCenterShift(dir, AABBCenter), dir, length, width);
        return rect;
    }

};

std::tuple<int, int, int, int> get_hit_probabilities(
        int iterations, 
        int seed, 
        float AABBHalfSize_x, 
        float AABBHalfSize_y, 
        float AABBCenter_x, 
        float AABBCenter_y, 
        float dir_x, 
        float dir_y, 
        float AABBCoef, 
        float dispersion, 
        float areaDamage
    ) {

    Vector2 AABBCenter = Vector2(AABBCenter_x, AABBCenter_y), 
        AABBHalfSize = Vector2(AABBHalfSize_x, AABBHalfSize_y), dir = Vector2(dir_x, dir_y);

    if (iterations < 1)
        return std::make_tuple(0, 0, 0, 0);

    int hits = 0, bounceOffs = 0, areaDamages = 0, misses = 0;

    SRect rect_full = SRect::GetUnitRect(AABBHalfSize, AABBCenter, dir);
    SRect rect_scaled = SRect::GetUnitRect(AABBHalfSize, AABBCenter, dir);
    rect_scaled.Compress(AABBCoef);
    
    RandomGen::InitSeed((unsigned int)seed);

    for (int i = 0; i < iterations; i++) {
        Vector2 hitPoint = RandomGen::RandQuardInCircle(dispersion);
        if (rect_scaled.IsPointInside(hitPoint)) {
            hits++;
            continue;
        }
        if (rect_full.IsPointInside(hitPoint)) {
            bounceOffs++;
            continue;
        }
        if (rect_scaled.IntersectsWithCircle(hitPoint, areaDamage)) {
            areaDamages++;
            continue;
        }
        misses++;
    }

    return std::make_tuple(hits, bounceOffs, areaDamages, misses);
}

float get_average_amount_of_shots_need_for_kill(
        int iterations, 
        int seed, 
        float hitChance, 
        float areaChance, 
        float areaDamageCoef, 
        float hpOriginal, 
        float damageMin, 
        float damageMax
    ) {
    
    int sum = 0;

    RandomGen::InitSeed((unsigned int)seed);

    for (int i = 0; i < iterations; i++) {
        float hp = hpOriginal;
        int count = 0;
        while (hp > 0) {
            float hitRng = RandomGen::RandomFloat01();
            if (hitRng <= areaChance) {
                hp -= (damageMin + (damageMax - damageMin) * RandomGen::RandomFloat01())
                    * areaDamageCoef;
            }
            else if (hitRng <= areaChance + hitChance) {
                hp -= (damageMin + (damageMax - damageMin) * RandomGen::RandomFloat01());
            }
            count++;
        }
        sum += count;
    }

    return float(sum) / iterations;
}

std::tuple<int, int> get_unit_vs_unit_comparison(
        int iterations, 
        int seed, 
        float unit1Hp,
        float unit2Hp,
        float unit1HitChance,
        float unit2HitChance,
        float unit1AreaChance,
        float unit2AreaChance,
        float unit1DamageMin,
        float unit2DamageMin,
        float unit1DamageMax,
        float unit2DamageMax,
        float unit1AimTime,
        float unit2AimTime,
        float unit1RelaxTime,
        float unit2RelaxTime,
        float unit1FireRate,
        float unit2FireRate,
        int unit1AmmoPerBurst,
        int unit2AmmoPerBurst,
        float areaDamageCoef
    ) {

    if (iterations < 1) {
        return std::make_tuple(0, 0);
    }

    int unit1_wins = 0, unit2_wins = 0;

    RandomGen::InitSeed((unsigned int)seed);

    // if unit2 has no weapon
    if (unit2AimTime < 0) {
        if (unit1HitChance > 0 && unit1DamageMax > 0) {
            unit1_wins = iterations;
            return std::make_tuple(unit1_wins, unit2_wins);
        }
        if (unit1AreaChance > 0 && unit1DamageMax > 0) {
            unit1_wins = iterations;
            return std::make_tuple(unit1_wins, unit2_wins);
        }
        return std::make_tuple(unit1_wins, unit2_wins);
    }

    const int BK2_TICKRATE = 20;
    const float BK2_TICKTIME = 1.0 / BK2_TICKRATE;

    //unit1AimTime = std::ceil(unit1AimTime * BK2_TICKRATE) / BK2_TICKRATE;
    //unit2AimTime = std::ceil(unit2AimTime * BK2_TICKRATE) / BK2_TICKRATE;

    //unit1RelaxTime = std::ceil(unit1RelaxTime * BK2_TICKRATE) / BK2_TICKRATE;
    //unit2RelaxTime = std::ceil(unit2RelaxTime * BK2_TICKRATE) / BK2_TICKRATE;

    auto simulate_hit = [&]
            (float& defender, const float attackerHitChance, const float attackerAreaChance, 
            const float attackerDamageMin, const float attackerDamageMax) {
            float hitRng = RandomGen::RandomFloat01();
            if (hitRng < attackerAreaChance) {
                // area dmg
                defender -= 
                    RandomGen::RandomFloatRange(attackerDamageMin, attackerDamageMax)
                    * areaDamageCoef;
                return;
            }
            else if (hitRng <= attackerAreaChance + attackerHitChance) {
                // full dmg
                defender -= RandomGen::RandomFloatRange(attackerDamageMin, attackerDamageMax);
                return;
            }
            // no dmg
            return;
    };

    for (int i = 0; i < iterations; i++) {

        float unit1 = unit1Hp;
        float unit2 = unit2Hp;

        float unit1Timer = unit1AimTime;
        float unit2Timer = unit2AimTime;

        unit1Timer = std::ceil(unit1Timer * BK2_TICKRATE) / BK2_TICKRATE;
        unit2Timer = std::ceil(unit2Timer * BK2_TICKRATE) / BK2_TICKRATE;

        int unit1Burst = unit1AmmoPerBurst;
        int unit2Burst = unit2AmmoPerBurst;

        while (unit1 > 0 && unit2 > 0) {

            float shooter = std::min(unit1Timer, unit2Timer);

            if (floatEquals(shooter, unit1Timer)) {

                simulate_hit(
                    unit2, unit1HitChance, unit1AreaChance, unit1DamageMin, unit1DamageMax
                );

                //update timer
                unit1Burst--;
                if (unit1Burst < 1) {
                    unit1Timer += unit1RelaxTime;
                    unit1Burst = unit1AmmoPerBurst;
                }
                else {
                    unit1Timer += 60.0f / unit1FireRate;
                }
                unit1Timer = std::ceil(unit1Timer * BK2_TICKRATE) / BK2_TICKRATE;
            }

            if (floatEquals(shooter, unit2Timer)) {

                simulate_hit(
                    unit1, unit2HitChance, unit2AreaChance, unit2DamageMin, unit2DamageMax
                );

                //update timer
                unit2Burst--;
                if (unit2Burst < 1) {
                    unit2Timer += unit2RelaxTime;
                    unit2Burst = unit2AmmoPerBurst;
                } else {
                    unit2Timer += 60.0f / unit2FireRate;
                }
                unit2Timer = std::ceil(unit2Timer * BK2_TICKRATE) / BK2_TICKRATE;
            }

        }

        if (unit1 <= 0)
            unit2_wins++;

        if (unit2 <= 0)
            unit1_wins++;

    }

    return std::make_tuple(unit1_wins, unit2_wins);

}

namespace py = pybind11;

PYBIND11_MODULE(aabb_hit_calc, m) {
    m.doc() = R"pbdoc(
        Pybind11 AABB Hits Calculation
        -----------------------

        .. currentmodule:: aabb_calculation

        .. autosummary::
           :toctree: _generate

           get_hit_probabilities
           get_average_amount_of_shots_need_for_kill
    )pbdoc";

    m.def("get_hit_probabilities", &get_hit_probabilities, R"pbdoc(
        Calculates the probabilites for hitting AABB

        It returns tuple[int, int, int, int].
    )pbdoc");

    m.def("get_average_amount_of_shots_need_for_kill", &get_average_amount_of_shots_need_for_kill, R"pbdoc(
        Calculates the average amount of shots needed for killing the target

        It returns a float.
    )pbdoc");

#ifdef VERSION_INFO
    m.attr("__version__") = MACRO_STRINGIFY(VERSION_INFO);
#else
    m.attr("__version__") = "dev";
#endif
}
