import { WebSocketServer } from "ws";
import { createServer } from "http";
import express from "express";
import handle_connection from "./connect.js";
const app = express();
app.use("/", express.static("static"));
const server = createServer(app);
const wss = new WebSocketServer({ server });
wss.on("connection", function (ws) {
	ws.on("message", function (message) {
		const data = String(Buffer.from(message));
		console.log(data);
	})
	ws.send("hello");
});
server.listen(8000, "127.0.0.1");

