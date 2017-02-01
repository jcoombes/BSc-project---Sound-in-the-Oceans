import numpy as np
import subprocess
import matplotlib.pyplot as plt

## setting up arrays to print in a ram in file
parameters0 = np.zeros((1,3))
parameters0[0,1] = 5.0
##############
parameters1 = np.zeros((1,3))
parameters1[0,0] = 50000.
parameters1[0,1] = 20.
parameters1[0,2] = 1
##############
# Receiver depth range
parameters2 = np.zeros((1,4))
parameters2[0,0] = 8000.
parameters2[0,1] = 1.0 
parameters2[0,2] = 1
parameters2[0,3] = 200.
##############
parameters3 = np.zeros((1,4))
parameters3[0,0] = 1600.
parameters3[0,1] = 8
parameters3[0,2] = 1
parameters3[0,3] = 0.
##############
parameters4 = np.zeros((3,2))
parameters4[0,0] = 0.
parameters4[0,1] = 2000. 
parameters4[1,0] = 25000.
parameters4[1,1] = 2000.
parameters4[2,0] = 50000.
parameters4[2,1] = 2000.
##############
parameters5 = np.zeros((1,2))
parameters5[0,0] = -1
parameters5[0,1] = -1
##############
parameters6 = np.zeros((1,2))
parameters6[0,0] = -1
parameters6[0,1] = -1 
##############
parameters7 = np.zeros((1,2))
parameters7[0,0] = 0.
parameters7[0,1] = 1700.
##############
parameters8 = np.zeros((1,2))
parameters8[0,0] = -1
parameters8[0,1] = -1
##############
parameters9 = np.zeros((1,2))
parameters9[0,0] = 0.
parameters9[0,1] = 1.5
##############
parameters10 = np.zeros((1,2))
parameters10[0,0] = -1
parameters10[0,1] = -1 
##############
parameters11 = np.zeros((3,2))
parameters11[0,0] = 0.
parameters11[0,1] = 0.5
parameters11[1,0] = 9000.
parameters11[1,1] = 0.5
parameters11[2,0] = 10000.
parameters11[2,1] = 10.
##############
parameters12 = np.zeros((1,2))
parameters12[0,0] = -1
parameters12[0,1] = -1

def Coppen(D,S,t):
    """
    Inputs:
        D - array, depth in kilometres
        S - array, salinity in parts per thousand
        t - array, T/10 where T = temperature in degrees Celsius
        
    Returns:
        v - array, sound velocity.
    """
    D=D/1000.
    t=t/10.
    A=(16.23+0.253*t)*D+(0.213-0.1*t)*D**2+(0.016+0.0002*(S-35))*(S-35)*t*D
    B=1449.05+45.7*t-5.21*t**2+0.23*t**3+(1.333-0.126*t+0.009*t**2)*(S-35)
    return A+B

depths = np.loadtxt('NS_HYCOM_depth.txt',delimiter=',')
salinity = np.loadtxt('NS_HYCOM_salt.txt',delimiter=',')
Temperature = np.loadtxt('NS_HYCOM_temp.txt',delimiter=',')
speed = Coppen(depths,salinity,Temperature)
def Ramin(speed, frequency=20,rd=20):
    """
    Writes the ram.in text file for the ram.exe model.
    
    Inputs:
        rd - receiver depth in meters
    Returns:
        a Ram.in file 
    """
    parameters0[0,0] = frequency
    parameters0[0,2] = rd
    NAMES  = np.array(["Auto generated ram.in; day 5112, frequency 20Hz"])
    np.savetxt('ram.in',NAMES,fmt='%s')
    temp = file('ram.in','a')
    np.savetxt(temp,parameters0,fmt ='%f')
    np.savetxt(temp,parameters1,fmt ='%f %f %i' )
    np.savetxt(temp,parameters2,fmt ='%f %f %i %f')
    np.savetxt(temp,parameters3,fmt ='%f %i %i %f')
    np.savetxt(temp,parameters4,fmt ='%f')
    np.savetxt(temp,parameters5,fmt ='%i')
    np.savetxt(temp,np.column_stack((depths,speed)),fmt='%f')
    np.savetxt(temp,parameters6,fmt ='%i')
    np.savetxt(temp,parameters7,fmt ='%f')
    np.savetxt(temp,parameters8,fmt ='%i')
    np.savetxt(temp,parameters9,fmt ='%f')
    np.savetxt(temp,parameters10,fmt ='%i')
    np.savetxt(temp,parameters11,fmt ='%f')
    np.savetxt(temp,parameters12,fmt ='%i')
    temp.close()


def output(fr,rd,N,speed_day):
    Data = np.arange(20,50020,20) 
    Title = np.array(["Data of day %s,at Depth %s of frequency from %s to %s Hz with an increment of %s"%(speed_day+1,rd,fr[0],fr[1],N)])
    np.savetxt('%s.txt'%(speed_day+1),Title,fmt='%s')
    fre = np.arange(fr[0],fr[1],N)
    for i in fre:
        Ramin(speed[speed_day], frequency=i,rd=rd)
        subprocess.call('ram.exe')# might potentially use the old tl.line
        tmp=np.loadtxt('tl.line')
        Data = np.column_stack((Data,tmp[:,1]))
    tmp1 = file('%s.txt'%(speed_day+1),'a')
    np.savetxt(tmp1,Data,fmt ='%f')
    tmp1.close()
    


def two_output(fr,N,speed_day,plot=False):
    fre = np.arange(fr[0],fr[1],N)
    Data = np.arange(20,50020,20)
    Title = np.array(["Data of day %s,Averaged over Depth 200mof frequency from %s to %s Hz with an increment of %s"%(speed_day+1,fr[0],fr[1],N)])
    np.savetxt('%s.txt'%(speed_day+1),Title,fmt='%s')
    for i in fre:
        Ramin(speed[speed_day], frequency=i)
        subprocess.call('ram.exe')# might potentially use the old tl.line
        # open the tl.grid file for plotting
        f = open('tl.grid','rb')
        
        # read in the data as floats. Some numbers were written as ints, so need to do two reads to get all the data we want.
        TL_data = np.fromfile(f,dtype='float32',count=-1)
        f.close()


        f = open('tl.grid','rb')
        TL_data_int = np.fromfile(f,dtype='int',count=-1)
        f.close()
        #The file contains a header, we need to extract some key quantities from the header
    
        frequency = TL_data[1]
        source_depth = TL_data[2]
        max_range = TL_data[4]
        range_step = TL_data[5]
        range_step_printing_freq = TL_data_int[6]
        depth_step = TL_data[8]
        depth_step_printing_freq = TL_data_int[9]
        depth_of_domain_printed = TL_data[10]
    

        number_of_ranges = (max_range / range_step) / range_step_printing_freq
        number_of_depths = (depth_of_domain_printed / depth_step) / depth_step_printing_freq
        
        #convert to ints
        number_of_ranges = int(number_of_ranges)
        number_of_depths = int(number_of_depths)
        
        # Allows double check    
        print 'Number of ranges to plot:',number_of_ranges
        print 'Number of depths of plot:',number_of_depths
    
        # create array to hold data to plot
        TL_to_plot = np.zeros((number_of_depths, number_of_ranges))
    

        for depth_count in range(0,number_of_depths):
            for range_count in range(0,number_of_ranges):
                TL_to_plot[depth_count,range_count] = TL_data[18+(range_count*(number_of_depths+2))+depth_count]
          
        Data = np.ma.row_stack((Data,np.mean(TL_to_plot,axis=0)))
    tmp2 = file('%s.txt'%(speed_day+1),'a')
    np.savetxt(tmp2,Data,fmt ='%f')
    tmp2.close()
    
    
    if plot == True:
        sound_vel_definitions = np.column_stack((speed[speed_day],-depths))
            
        
        # Plot
        plt.matshow(TL_to_plot,interpolation='none',extent=[0,max_range,depth_of_domain_printed*-1,0], aspect = 10, vmin = 40, vmax = 120)
        plt.colorbar(orientation='horizontal',label='Transmission Loss (dB re 1m)')
        plt.xlabel('Range (m)')
        plt.ylabel('Depth (m)')
        plt.ylim(-1*depth_of_domain_printed,0)
        plt.text(500,(depth_of_domain_printed *(11.0/40.0)),"Frequency = %d Hz" % frequency, size = 11)
        plt.text(500,(depth_of_domain_printed *(6.0/40.0)),"Source Depth = %d m" % source_depth, size = 11)
            
        # plot sound speed profile

        plt.figure(2)
        plt.plot(sound_vel_definitions[:,0],sound_vel_definitions[:,1],c='black')
        plt.ylabel('Depth (m)')
        plt.xlabel('Sound speed $\mathregular{(ms^{-1}\!)}$')
        plt.show()
      
