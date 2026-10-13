// Current frame sent to client:
// {
//     int32 RaceTime [ms]
// }
// sum = 4 bytes
// port is set via /configstring="set jatb_port <port>"

Net::Socket@ server = null;
Net::Socket@ client = null;

const string HOST = "127.0.0.1";
uint16 PORT;

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

void OnRunStep(SimulationManager@ sim) {
    if (@client is null || !sim.InRace) {
        return;
    }

    bool ok = client.Write(int(sim.RaceTime));

    if (!ok) {
        log("JATB client disconnected");
        @client = null;
    }
}

// keep Accept here because it's non-blocking and also in menu
void Render() {
    if (@server is null) {
        return;
    }

    auto@ s = server.Accept(0);

    if (@s !is null) {
        @client = s;
        client.NoDelay = true;
        log ("JATB client conneted " + client.RemoteIP);
    }
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
