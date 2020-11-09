import os, time, threading, cv2, queue

# Use semaphores for frame handling
wait = threading.BoundedSemaphore(10)
fill = threading.BoundedSemaphore(10)

# Semaphore 
sem = threading.BoundedSemaphore(10)
sem2 = threading.BoundedSemaphore(10)

#Queues for frame storage
q = queue.Queue()
q2 = queue.Queue()



class ExtractFrames(threading.Thread):            

    def __init__(self):
        threading.Thread.__init__(self)
        for i in range(10):
            # lock starts to extract frames
            fill.acquire()
            # lock wait for frames to extract 
            wait.acquire()            

    def run(self):
        # Global vars 
        outputDir    = 'frames'
        clipFileName = 'clip.mp4'
        
        mutex = threading.Lock()                        
        # Initialize frame count
        count = 0

        # open video clip
        vidcap = cv2.VideoCapture(clipFileName)
        
        # create the output directory if it doesn't exist
        if not os.path.exists(outputDir):
            print("Output directory {} didn't exist, creating".format(outputDir))
            os.makedirs(outputDir)

        # read one frame
        success,image = vidcap.read()
        # Start queue  count 
        countQueue = 0

        print("Reading frame {} {} ".format(count, success))
        while success:
            
          sem.acquire()
          mutex.acquire()
      
          q.put(image)

          # Read one frame 
          success,image = vidcap.read()

          print('Reading frame {}'.format(count))
    

          count += 1
          for i in range(10):
            countQueue+=1
     
          if(q.empty()):
              if(q2.empty()):
                  sem.release()
                  fill.release()
                  print("exit")
                  break
          mutex.release()
          fill.release()


class ConvertToGrayscale(threading.Thread):


    def __init__(self):
        threading.Thread.__init__(self)
     
    def run(self):
       
        count = 0
        n = 0
        countQueue = 0
        while True:
            fill.acquire()                        
            sem2.acquire()
       
            print("Converting frame {}".format(count))

            # convert the image to grayscale
            grayscaleFrame = cv2.cvtColor(q.get(), cv2.COLOR_BGR2GRAY)

            count += 1
            q2.put(grayscaleFrame)
            for i in range(10):
                i+=1
       
            if(q.empty()):
                if(q2.empty()):
                    print("exit2")
                    sem2.release()
                    wait.release()
                    sem.release()
                    break
            wait.release()
            sem.release()
        for i in range(9):
            wait.release()

        fill.release()


class DisplayFrames(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        count = 0
        countQueue = 0
        while True:
            wait.acquire()
    
            img = q2.get()

            print("Displaying frame {}".format(count))
            time.sleep(.042)                                                
            cv2.imshow("Video", img)
            if cv2.waitKey(42) and 0xFF == ord("q"):
                break
     
            count += 1
            for i in range(10):
                countQueue+=1
            sem2.release()
            if (q.empty()):
                if q2.empty():
                    break
    
        wait.release()
      
        print("Finished displaying all frames")
        
        # cleanup windows
        cv2.destroyAllWindows()
        exit()

extract = ExtractFrames()
convert = ConvertToGrayscale()
display = DisplayFrames()

extract.start()
convert.start()
display.start()
