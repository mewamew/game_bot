const mineflayer = require('mineflayer')
const { pathfinder, Movements, goals } = require('mineflayer-pathfinder')
const express = require('express')
const app = express()
app.use(express.json())

const bot = mineflayer.createBot({
  host: 'localhost', // minecraft 服务器的 IP 地址
  username: 'botbot', // minecraft 用户名
  port: 28888,                // 默认使用 25565，如果你的服务器端口不是这个请取消注释并填写。
})

bot.loadPlugin(pathfinder)


bot.once('login', () => {
  console.log('hello');
  bot.on('chat', (username, message) => {
    if (username === bot.username) return
    if (message === 'come') {
      bot.chat("我来咯！")
      const follow = () => {
        const target = bot.players[username] ? bot.players[username].entity : null
        if (!target) {
          bot.chat("我找不到你。")
          return
        }
        const { x, y, z } = target.position
        const movements = new Movements(bot, require('minecraft-data')(bot.version))
        bot.pathfinder.setMovements(movements)
        bot.pathfinder.setGoal(new goals.GoalNear(x, y, z, 1), true)
        
        // 每5秒跟踪一次
        const intervalId = setInterval(() => {
          const newTarget = bot.players[username] ? bot.players[username].entity : null
          if (!newTarget) {
            bot.chat("我找不到你。")
            clearInterval(intervalId)
            return
          }
          const { x: newX, y: newY, z: newZ } = newTarget.position
          bot.pathfinder.setGoal(new goals.GoalNear(newX, newY, newZ, 1), true)
        }, 5000)
      }
      follow()
    }
  })
  // 记录错误和被踢出服务器的原因:
  bot.on('kicked', console.log)
  bot.on('error', console.log)
})

app.post('/chat', (req, res) => {
    const message = req.body.message
    if (message) {
      bot.chat(message)
      res.send('Message sent')
      bot.swingArm('right')
    }
  })

app.listen(3000, () => {
  console.log('Chat server listening on port 3000')
})
