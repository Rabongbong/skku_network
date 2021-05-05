import sys
import socket
from logHandler import logHandler
import time


def receiveACK(senderSocket):
  global windowSize
  global checkAck
  global sendBuffer
  pdb.set_trace()
  newMsg, recvAddr= senderSocket.recvfrom(1400)
  ACK =  newMsg.decode()
  lock.acquire()
  logProc.writeAck(ACK, 'received')
  lock.release()
  for i in range(0, ACK):
    del sendBuffer[i]
  lock.acquire()
  windowSize+=1
  lock.release()
  


def fileSender(recvAddr, windowSize, srcFilename, dstFilename):

  logProc = logHandler()
  throughput = 0.0
  avgRTT = 10.0

  ##########################
  serverPort = 10080  #port
  senderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	
  serialNumber=0
  sendBuffer={}    # 파일에서 읽어오는 내용은 list에 저장
  checkACK={}      # check ACK is arrived or not
  checkTime={}     # check time(packet)
  flag=1           # 파일을 다 읽었는지 여부 표시
  

  logProc.startLogging("testSendLogFile.txt")
  sendfile = open(srcFilename, 'rb')
  
  # 초기에 packet 보내기
  while windowSize!=0:
    if serialNumber == 0:
      resHeader += dstFilename
      resHeader += str(serialNumber)
      fileData = sendfile.read(1400-len(resHeader))
      sendData = resHeader.encode()
      sendData += fileData
      sendBuffer[serialNumber]=sendData
      senderSocket.sendto(sendData, (recvAddr, serverPort))
      lock.acquire()
      logProc.writePkt(serialNumber, 'sent')
      lock.release()
      windowSize -= 1
      serialNumber += 1
    else:
      resHeader += str(serialNumber)
      fileData = sendfile.read(1400-len(resHeader))
      sendData = resHeader.encode()
      sendData += fileData
      sendBuffer[serialNumber]=sendData
      senderSocket.sendto(sendData, (recvAddr, serverPort))
      lock.acquire()
      logProc.writePkt(serialNumber, 'sent')
      lock.release()
      windowSize -= 1
      serialNumber += 1


  while True:
    newMsg, recvAddr= senderSocket.recvfrom(1400)

    if serialNumber == 0:
      resHeader += dstFilename
      resHeader += str(serialNumber)
      fileData = sendfile.read(1400-len(resHeader))
      sendData = resHeader.encode()
      sendData += fileData
      sendBuffer[serialNumber]=sendData
      senderSocket.sendto(sendData, (recvAddr, serverPort))
      lock.acquire()
      logProc.writePkt(serialNumber, 'sent')
      windowSize -= 1
      serialNumber += 1
      lock.release()

      else:
        resHeader += str(serialNumber)
        fileData = sendfile.read(1400-len(resHeader))
        sendData = resHeader.encode()
        sendData += fileData
        sendBuffer[serialNumber]=sendData
        senderSocket.sendto(sendData, (recvAddr, serverPort))
        lock.acquire()
        logProc.writePkt(serialNumber, 'sent')
        windowSize -= 1
        serialNumber += 1
        lock.release()

      if fileData =="":
        flag=0
        sendfile.close()
        break
    
    if flag ==0:
      break
      # logProc.writeEnd(throughput, avgRTT)
    ##########################


if __name__=='__main__':
  lock = threading.Lock()
  recvAddr = sys.argv[1]  #receiver IP address
  windowSize = int(sys.argv[2])   #window size
  srcFilename = sys.argv[3]   #source file name
  dstFilename = sys.argv[4]   #result file name
  fileSender(recvAddr, windowSize, srcFilename, dstFilename)