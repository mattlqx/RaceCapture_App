package com.autosportlabs.racecapture;
import android.location.LocationListener;
import android.os.Looper;
import android.location.LocationManager;
import android.content.Context;
import android.util.Log;
import android.os.Bundle;
import android.location.Location;
import org.kivy.android.PythonActivity;
/**
 * GPS connection bridge for RaceCature app
 * @author brent
 *
 */


public class GpsConnection implements LocationListener{
	
	static GpsConnection g_instance = null;
	LocationManager locationManager = null;
	Location currentLocation = null;
	int currentStatus = 0;
	boolean providerEnabled = false;
	
	static public GpsConnection createInstance(){
		if (g_instance == null){
			g_instance = new GpsConnection();
		}
		return g_instance;
	}	
		
	public Location getCurrentLocation(){
		return this.currentLocation;
	}
	
	public int getCurrentStatus(){
		return currentStatus;
	}
	
	public boolean getProviderEnabled(){
		return this.providerEnabled;
	}
	
	public void onLocationChanged(Location location) {
		this.currentLocation = location;
	}
	
	public void onStatusChanged(String provider, int status, Bundle extras) {
		/* 0x00 = out of service
		 * 0x01 = temporarily unavailable
		 * 0x02 = available
		 */
		this.currentStatus = status;
	}
	
	public void onProviderEnabled(String provider) {
		this.providerEnabled = true;
	}
	
	public void onProviderDisabled(String provider) {
		this.providerEnabled = false;
	}
	
	public boolean configure(){
		try{
			locationManager = (LocationManager)PythonActivity.mActivity.getSystemService(Context.LOCATION_SERVICE);
			return true;
		}
		catch(Exception e){
			Log.i("Message: ", "failed to get Android Location Service: " + e.toString());
			return false;
		}
	}
	
	public boolean start(){
		try{
			locationManager.requestLocationUpdates(LocationManager.GPS_PROVIDER,1000,0, this, Looper.getMainLooper());
			return true;
		}
		catch(Exception e){
			Log.i("Message: ", "failed to enable GPS location updates: " + e.toString());
			return false;
		}
	}
	
	public void stop(){
		locationManager.removeUpdates(this);
	}
}
