mod general_bus {
	pub mod prelude {
		#![allow(unused)]
		pub trait BusType {
			type BusAdress;
			type BusData;
			type BusErr;
		}
		pub trait Bus: BusType {
			fn read(&self, add: Self::BusAdress) -> Result<Self::BusData, Self::BusErr>;
			fn load(&mut self, add: Self::BusAdress, src: Self::BusData) -> Option<Self::BusErr>;
		}
		#[derive(Debug)]
		pub enum AcessErr {
			Underflow,
			Overflow,
			InvalidRange,
			CannotAcess
		}
		#[derive(Debug)]
		pub enum VirtualErr<E, I> {
			External(E),
			Internal(I)
		}
		pub enum AcessType {
			Rx,
			Ex,
			Ro,
			Rw,
			Wo,
			Wx
		}
		pub trait AcessControl<T: BusType> where <T as BusType>::BusAdress: PartialOrd {
			//set acess type to underlying bus;
			fn set_acc(&mut self, src: AcessType);
			//set maximum acessible adress;
			fn set_max(&mut self, src: <T as BusType>::BusAdress);
			//set minimum acessible adress;
			fn set_min(&mut self, src: <T as BusType>::BusAdress);
			//get acess type police
			fn get_acc(&self) -> &AcessType;
			//check if adress is in a valid range 
			//(and thus the range itself);
			fn get_adr<'a>(&'a self) -> (
				&'a <T as BusType>::BusAdress, 
				&'a <T as BusType>::BusAdress
			);
			fn chk_adr(&self, adr: &<T as BusType>::BusAdress) -> Option<AcessErr> {
				let (max, min) = Self::get_adr(&self);
				if max < min {
					Some(AcessErr::InvalidRange)
				} else if max < adr {
					Some(AcessErr::Overflow)
				} else if min > adr {
					Some(AcessErr::Underflow)
				} else {
					None
				}
			}
			//check the acess direction (a subset of acess type);
			fn chk_dir(&self, dir: bool) -> bool {
				match Self::get_acc(self) {
					AcessType::Rw => true,
					AcessType::Ro | 
					AcessType::Rx => !dir,
					AcessType::Wo |
					AcessType::Wx => dir,
					_ => false
				}
			}
		}
		pub trait ExecControl<T: BusType>: AcessControl<T> where <T as BusType>::BusAdress: PartialOrd {
			//a complementar function which allows checking
			//if a memory is executable 
			//(if it has a underlying no-exec bit)
			fn chk_exe(&self, flag: bool) -> bool {
				match Self::get_acc(self) {
					AcessType::Rx | 
					AcessType::Ex => true,
					AcessType::Wx => flag,
					_ => false
				}
			}
		}
	}
	pub mod sync_recover {
		use std::sync::*;
	}
	pub mod mmut_wraper {
		#![allow(unused)]
		use std::ops::Deref;
		pub use std::sync::{Arc, RwLock};
		use std::sync::{RwLockWriteGuard, RwLockReadGuard};
		pub struct MMutWraper<T>(Arc<RwLock<T>>);
		impl<T> MMutWraper<T> {
			pub fn new(src: T) -> Self {
				Self(Arc::new(RwLock::new(src)))
			}
			pub fn dump(&self) -> Self {
				Self(self.0.clone())
			}
			pub fn dump_from(src: &Self) -> Self {
				Self::dump(src)
			}
			pub fn raw_read(&self) -> RwLockReadGuard<T>{
				self.0.read().unwrap()
			}
			pub fn raw_load(&self) -> RwLockWriteGuard<T>{
				self.0.write().unwrap()
			}
		}
		impl<T> Deref for MMutWraper<T> {
			type Target = Arc<RwLock<T>>;
			fn deref(&self) -> &Self::Target {
				&self.0
			}
		}
	}
	pub mod simple_ctlbus {
		#![allow(unused)]
		pub use super::prelude::*;
		pub use super::mmut_wraper::MMutWraper;
		use std::sync::RwLock;
		pub struct AcessControlUnit<B: Bus + BusType> {
			bus: MMutWraper<B>,
			max: <B as BusType>::BusAdress,
			min: <B as BusType>::BusAdress,
			acc: AcessType,
		}
		impl<B: BusType + Bus> AcessControl<B> for AcessControlUnit<B> 
		where <B as BusType>::BusAdress: PartialOrd {
			fn set_acc(&mut self, src: AcessType) {
				self.acc = src;
			}
			fn set_max(&mut self, src: <B as BusType>::BusAdress) {
				self.max = src;
			}
			fn set_min(&mut self, src: <B as BusType>::BusAdress) {
				self.min = src;
			}
			fn get_acc(&self) -> &AcessType {
				&self.acc
			}
			fn get_adr<'a>(&'a self) -> (
			&'a <B as BusType>::BusAdress, 
			&'a <B as BusType>::BusAdress) {
				(&self.max, &self.min)
			}
		}
		impl<B: Bus + BusType> BusType for AcessControlUnit<B> {
			type BusAdress = <B as BusType>::BusAdress;
			type BusData = <B as BusType>::BusData;
			type BusErr = VirtualErr<<B as BusType>::BusErr, AcessErr>;
		}
		impl<B: Bus + BusType> Bus for AcessControlUnit<B> where <B as BusType>::BusAdress: PartialOrd {
			fn read(&self, add: Self::BusAdress) -> Result<Self::BusData, Self::BusErr> {
				AcessControl::<B>::chk_adr(self, &add).and_then(|x| Some(Err(VirtualErr::Internal(x))))//Option<Result<!, x>>
				.unwrap_or_else(|| {
					if AcessControl::<B>::chk_dir(self, false) {
						<B as Bus>::read(&RwLock::<B>::read(&self.bus).unwrap(), add).or_else(|e| Err(VirtualErr::External(e)))
					} else {
						Err(VirtualErr::Internal(AcessErr::CannotAcess))
					}
				})
			}
			fn load(&mut self, add: Self::BusAdress, src: Self::BusData) 
			-> Option<Self::BusErr> {
				AcessControl::<B>::chk_adr(self, &add).and_then(|e| 
				Some(VirtualErr::Internal(e))).or_else(|| {
					if AcessControl::<B>::chk_dir(self, true) {
						self.bus.write().unwrap().load(add, src)
							.and_then(|e| Some(VirtualErr::External(e)))
					} else {
						Some(VirtualErr::Internal(AcessErr::CannotAcess))
					}
				})
			}
		}
		impl<B: BusType + Bus> AcessControlUnit<B> where <B as BusType>::BusAdress: PartialOrd{
			pub fn new(bus: MMutWraper<B>, max: <B as BusType>::BusAdress, min: <B as BusType>::BusAdress, acc: AcessType) -> Self {
				Self {
					bus,
					max,
					min,
					acc,
				}
			}
		}
	}
	pub mod simple_bus {
		#![allow(unused)]
		use super::mmut_wraper::MMutWraper;
		use std::ops::Deref;
		use super::prelude::{Bus, BusType};
		pub struct SimpleBus {
			mem: MMutWraper<Vec<u8>>
		}
		#[derive(Debug)]
		pub enum SimpleBusErr {
			OutOfBondary
		}
		impl BusType for SimpleBus {
			type BusAdress = usize;
			type BusData = u8;
			type BusErr = SimpleBusErr;
		}
		impl Bus for SimpleBus {
			fn read(&self, add: Self::BusAdress) -> Result<Self::BusData, Self::BusErr> {
				self.mem.read().unwrap().get(add).and_then(|x| Some(*x))
					.ok_or(SimpleBusErr::OutOfBondary)
			}
			fn load(&mut self, add: Self::BusAdress, src: Self::BusData) -> Option<Self::BusErr> {
				match self.mem.write().unwrap().get_mut(add) {
					Some(d) => {*d = src; None},
					None => Some(SimpleBusErr::OutOfBondary)
				}
			}
		}
		impl SimpleBus {
			pub fn new(src: MMutWraper<Vec<u8>>) -> Self {
				Self {
					mem: src.dump()
				}
			}
		}
		impl Deref for SimpleBus {
			type Target = MMutWraper<Vec<u8>>;
			fn deref(&self) -> &Self::Target {
				&self.mem
			}
		}
	}
	pub mod tests {
		pub mod test_1 {
			
		}
	}
}

use general_bus::{simple_ctlbus::*, simple_bus::SimpleBus};
use std::thread;
fn main () {
    let raw_mem: Vec<u8> = vec![0; 5];
    let mem: MMutWraper<Vec<u8>> = MMutWraper::new(raw_mem);
    let my_bus = MMutWraper::new(SimpleBus::new(mem));
    let mut hand = vec![];
    for x in 0..5 {
        let mut my_mmu = AcessControlUnit::new(MMutWraper::dump_from(&my_bus), 30, 2, AcessType::Ex);
        let th = thread::spawn(move || {
            for _ in 0..50 {

            }
            for z in 0..20 {
                println!("[Read] thread {x:0>2} at {z:0>2} : {}", match my_mmu.read(z) {
                    Ok(d) => format!("{d:0>2}"),
                    Err(e) => format!("Error: {:?}", e)
                });
                println!("[Load] thread {x:0>2} at {z:0>2} : {}", 
                    my_mmu.load(z, (z + 20 * x) as u8).and_then(|e| {
					if z == 10 && x > 2 {
						panic!("{x}")
					};
                    Some(format!("Error: {:?}", e))
					}).unwrap_or("Ok".to_string()));
                for _ in 0..50 {

                }
            }
        });
        hand.push(th);
    }
    for th in hand {
        th.join();
    }
    println!("{:?}", my_bus.raw_read().raw_read().to_vec());
}