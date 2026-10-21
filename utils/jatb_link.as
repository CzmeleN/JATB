// Current frame sent to client:
// {
//     int32    FrameId             
//     int32    RaceTime              [ms]
//     int32    RaceFinished          [0/1]
//<----int32    GameState             [TM::GameState]---->
//     float32  Velocity[3]           [m/s]
//     float32  CurrentLocalSpeed[3]  [m/s]
//     float32  Rotation[9]
//     float32  AngularSpeed[3]
//     int32    Gear
//     float32  TurningRate
// }
// sum = 4 + 4 + 4 + 12 + 12 + 36 + 12 + 4 + 4 = 92 bytes
// port is set via /configstring="set jatb_port <port>"

// Frame received from client:
// {
//     uint8   Type
//     uint16  Len
//     uint8   Payload[Len]
// }
// Types:
// 1 SET_GAS    int32 accel [-65536, 65536]  : 4B
// 2 SET_STEER  int32 steer [-65536, 65536]  : 4B
// 3 RESTART                                 : 0B
// 4 EXECUTE    console command              : ?B
enum MsgType {
    SetGas   = 1,
    SetSteer = 2,
    Restart  = 3,
    Execute  = 4
}

int frameId = 0;
int pendingType = -1; // waiting for header
uint pendingLen = 0;
array<string> commQueue;

Net::Socket@ server = null;
Net::Socket@ client = null;

const string HOST = "127.0.0.1";
uint16 PORT;

void ResetConnState() {
    pendingType = -1;
    pendingLen = 0;
}

void HandleMessages() {
    while (@client !is null) {
        if (pendingType < 0) {
            if (client.Available < 3) {
                return;
            }

            pendingType = client.ReadUint8();
            pendingLen = client.ReadUint16();
        }

        if (client.Available < pendingLen) {
            return; // retry
        }

        Dispatch(pendingType, pendingLen);
        pendingType = -1;
    }
}

void Dispatch(int type, uint len) {
    if (((type == MsgType::SetGas || type == MsgType::SetSteer) && len != 4) ||
        (type == MsgType::Restart && len != 0)) {
        if (len > 0) {
            client.ReadBytes(len);
        }

        log("JATB bad length " + len + " for type " + type, Severity::Warning);

        return;
    }

    auto@ sim = GetSimulationManager();

    switch (type) {
        case MsgType::SetGas: {
            const int gas = client.ReadInt32();

            if (sim.InRace) {
                sim.SetInputState(InputType::Gas, Math::Clamp(gas, -65536, 65536));
            }

            break;
        }
        case MsgType::SetSteer: {
            const int steer = client.ReadInt32();

            if (sim.InRace) {
                sim.SetInputState(InputType::Steer, Math::Clamp(steer, -65536, 65536));
            }

            break;
        }
        case MsgType::Execute: {
            commQueue.Add(client.ReadString(len));

            break;
        }
        case MsgType::Restart: {
            if (sim.InRace) {
                sim.GiveUp();
            }

            break;
        }
        default: {
            if (len > 0) {
                client.ReadBytes(len);
            }

            log("JATB unknown message type " + type, Severity::Warning);

            break;
        }
    }
}

void Init() {
    if (@server is null) {
        @server = Net::Socket();

        log("Opened JATB socket on " + PORT);

        if (server.Listen(HOST, PORT)) {
            log("JATB listening on 127.0.0.1:" + PORT);
        } else {
            log("JATB cannot listen on port " + PORT, Severity::Error);
            @server = null;
        }
    }
}

bool WriteVec3(const vec3&in v) {
    return client.Write(v.x) && client.Write(v.y) && client.Write(v.z);
}

void OnRunStep(SimulationManager@ sim) {
    if (@client is null || !sim.InRace) {
        return;
    }

    HandleMessages();

    auto@ dyna = sim.Dyna;
    auto@ car = sim.SceneVehicleCar;
    const mat3 rot = dyna.CurrentState.Location.Rotation;

    bool ok = client.Write(frameId);
    ok = ok && client.Write(int(sim.RaceTime));
    ok = ok && client.Write(int((sim.PlayerInfo.RaceFinished || sim.TickTime > sim.RaceTime) ? 1 : 0));
    ok = ok && WriteVec3(dyna.CurrentState.LinearSpeed);
    ok = ok && WriteVec3(car.CurrentLocalSpeed);
    ok = ok && WriteVec3(rot.x) && WriteVec3(rot.y) && WriteVec3(rot.z);
    ok = ok && WriteVec3(dyna.CurrentState.AngularSpeed);
    ok = ok && client.Write(int(car.CarEngine.Gear));
    ok = ok && client.Write(car.TurningRate);

    if (!ok) {
        log("JATB client disconnected");
        @client = null;
        ResetConnState();
    }

    frameId++;
}

// keep Accept here because it's non-blocking
// everything in here works in menus and changing maps is better in here
void Render() {
    if (@server is null) {
        return;
    }

    auto@ s = server.Accept(0);

    if (@s !is null) {
        @client = s;
        client.NoDelay = true;
        ResetConnState();
        log ("JATB client conneted " + client.RemoteIP);
    }

    HandleMessages();

    for (uint i = 0; i < commQueue.Length; i++) {
        ExecuteCommand(commQueue[i]);
    }
    commQueue.Clear();
}

void Main() {
    RegisterVariable("jatb_port", 0);
    PORT = uint16(GetVariableDouble("jatb_port"));
    Init();
}

PluginInfo@ GetPluginInfo() {
    PluginInfo info;
    info.Author = "JATB";
    info.Name = "JATB Link";
    info.Description = "Communicate with a Linux client";
    info.Version = "0.1";
    return info;
}
