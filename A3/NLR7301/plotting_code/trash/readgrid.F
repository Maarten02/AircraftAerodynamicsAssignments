        program read
!
        real(kind=8) :: X(170,400,9),Y(170,400,9)
        integer      :: imax(9),jmax(9)

        open(unit=8,file='nlrgap13.dat',status='old')
!
        READ (8,*) nblock                                    
        DO nb=1,nblock
           READ (8,*) imax(nb),jmax(nb)                                        
           IL = imax(nb)
           JL = jmax(nb)
           DO j=1,JL
           DO i=1,IL
              READ (8,*) x(i,j,nb),y(i,j,nb) 
           END DO
           END DO
        END DO
!
        END
